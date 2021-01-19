# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals

import json
import os
import re
import subprocess
import sys
import warnings
import yaml

from pkg_resources import parse_version

TESTCASES = list()
INVENTORY = 'test/fixtures/hosts'

HERE = os.path.abspath(os.path.dirname(__file__))
ROLE = re.match(
    r'^.*\/ansible-eos-([^/\s]+)\/test/arista-ansible-role-test$', HERE).group(1)
RUN_CONFIG_BACKUP = '_eos_role_test_{}_running'.format(ROLE)
START_CONFIG_BACKUP = '_eos_role_test_{}_startup'.format(ROLE)

EOS_ROLE_PLAYBOOK = 'test/arista-ansible-role-test/eos_role.yml'
EOS_MODULE_PLAYBOOK = 'test/arista-ansible-role-test/eos_module.yml'

LOG_FILE = '{}/roletest.log'.format(HERE)
try:
    os.remove(LOG_FILE)
except OSError:
    pass

LOG = open(LOG_FILE, 'w')
SEPARATOR = '    ' + '*' * 50

# Because of changes between Ansible 2.1 and 2.2, let's
# keep track of what version we are working with.
# ANSIBLE_NEW is True if the version is 2.2 or later (assume true,
# will update during test setup)
# ANSIBLE_VERSION is the exact version string
ANSIBLE_NEW = False
ANSIBLE_VERSION = None


class TestCase(object):
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.module = kwargs['module']

        self.host = None

        self.inventory = kwargs.get('inventory')
        self.negative = kwargs.get('negative', False)
        self.idempotent = kwargs.get('idempotent', True)
        self.changed = kwargs.get('changed', True)
        self.present = kwargs.get('present')
        self.absent = kwargs.get('absent')

        self.arguments = kwargs.get('arguments', list())
        self.variables = dict()

        # optional properties
        self.setup = kwargs.get('setup', list())
        self.teardown = kwargs.get('teardown', list())

    def __str__(self):
        return self.name


class TestModule(object):
    def __init__(self, testcase):
        self.testcase = testcase
        self.description = 'Test [%s]: %s' % (testcase.module, testcase.name)

    def __call__(self):
        self.output('Run first pass')
        response = self.run_module()
        for device in response:
            hostname = device.keys()[0]
            reported = int(device[hostname]['changed'])
            expected = int(self.testcase.changed)
            msg = ("First pass role execution reported {} task change(s), "
                   "expected {}".format(reported, expected))
            self.output(msg)
            assert reported == expected, msg

        if self.testcase.idempotent:
            self.output('Run second pass')
            response = self.run_module()
            for device in response:
                hostname = device.keys()[0]
                reported = int(device[hostname]['changed'])
                msg = (
                    "Second pass role execution reported {} task change(s), "
                    "expected 0".format(reported))
                self.output(msg)
                assert not reported, msg

        if self.testcase.present:
            desc = 'Validate present configuration'
            self.output(desc)

            # # We need to handle things differently beginning with
            # # Ansible 2.2 and up.
            # if ANSIBLE_NEW:
            #     values = []
            #     # We need to break the 'present' configuration into
            #     # top level blocks. Use a regex to find top level
            #     # lines and their sub leve lines.
            #     matches = re.findall(r'^(\S.*\n)((\s+.*\n)*)',
            #                          self.testcase.present, re.M)
            #     if matches:
            #         for match in matches:
            #             if match[1]:
            #                 # A top level entry with sub level lines
            #                 # Split the sub level lines an strip leading spaces
            #                 values.append({
            #                     'lines': [l.lstrip() for l in match[1].splitlines()],
            #                     'parents': [match[0].rstrip('\n')]
            #                 })
            #             else:
            #                 # A single top level line
            #                 values.append({'lines': match[0]})
            # else:
            #     # Ansible 2.1 and earlier - just use the 'present' config
            #     values = [self.testcase.present]
            values = self.format_config_list(self.testcase.present)

            for value in values:
                # run_validation takes the config block itself for
                # Ansible 2.1 and earlier, and 'lines' and
                # optional 'parents' keys for 2.2 and later
                response = self.run_validation(value, desc=desc)
                for device in response:
                    hostname = device.keys()[0]
                    # Result should contain an empty list of updates
                    # XXX This appears to be broken in Ansible 2.2 --
                    # -- the task output returns some items in the
                    # -- updates dictionary, but the play recap
                    # -- indicates no changes. Skip updates check for 2.2
                    ansible_2_2 = (
                        parse_version(ANSIBLE_VERSION) >= parse_version('2.2') and
                        parse_version(ANSIBLE_VERSION) < parse_version('2.3')
                    )
                    # if not ANSIBLE_NEW:
                    if not ansible_2_2:
                        delim = " ---\n"
                        updates = device[hostname].get('updates', [])
                        msg = ("{} - Expected configuration\n{}{}\n{}"
                               "not found on device '{}'".
                               format(desc, delim, '\n'.join(updates),
                                      delim, hostname))
                        assert updates == [], msg
                    # Result should show no changes
                    msg = ("{} - Device '{}' reported no updates, but "
                           "returned 'changed'".format(desc, hostname))
                    assert not int(device[hostname]['changed']), msg

        if self.testcase.absent:
            desc = 'Validate absent configuration'
            self.output(desc)
            values = self.format_config_list(self.testcase.absent)

            for value in values:
                response = self.run_validation(value, desc=desc)
                for device in response:
                    hostname = device.keys()[0]
                    # Result should show change has taken place
                    msg = (
                        "{} - Entire absent configuration found "
                        "on device '{}'".
                        format(desc, hostname)
                    )
                    assert int(device[hostname]['changed']), msg

                    # Join the list of updates and remove trailing newline
                    updates = '\n'.join(device[hostname]['updates'])
                    updates = updates.rstrip('\n')
                    # The output from the playbook is sanitized - the phrase
                    # network-admin in username entries is changed to
                    # network-********. Replace the asterisks with admin again
                    # for matching the results.
                    updates = re.sub("username ([^\n]*) role network-\*{8}",
                                     r'username \1 role network-admin',
                                     updates)

                    # Format the absent list for comparison to the updates
                    # list. Make two lists: a list with the standard config
                    # indentation, and a second list with the indentation
                    # stripped. Later versions of Ansible began stripping
                    # the indentation from the updates list, so we need to
                    # compare the updates to both a standard format config
                    # and an indent-stripped format of the config.

                    if ANSIBLE_NEW:
                        # Ansible 2.2 uses parents and lines to construct
                        # the configuration. We need to join those back
                        # together to create a standard format config block.
                        absent = list(value.get('parents', []))
                        absent.extend(value['lines'])
                        absent = '\n'.join(absent)
                        # # Since Ansible 2.2 and later remove indentation,
                        # # we have already stripped the indentation from
                        # # the absent list. Set absent_stripped to the
                        # # absent string, just to be safe.
                        # absent_stripped = absent
                    else:
                        # Strip any trailing whitespace from the absent string
                        # This will be the standard format configuration
                        # of what should be absent on the switch
                        absent = value.rstrip()

                    absent_stripped = '\n'.join(map(str.lstrip, absent.split('\n'))).rstrip('\n')

                    msg = ("{} - Some part of absent configuration found "
                           "on device '{}'".format(desc, hostname))
                    assert (updates == absent) or (updates == absent_stripped), msg

    def setUp(self):
        print("\n{}\n".format(SEPARATOR) +
              "  See run log for complete output:\n  {}".format(LOG_FILE) +
              "\n{}\n".format(SEPARATOR))

        LOG.write("\n\n\n{}\n".format(SEPARATOR) +
                  "  Begin log for {}".format(self.description) +
                  "\n{}\n\n".format(SEPARATOR))

        if self.testcase.setup:
            self.output('Running test case setup commands')
            setup_cmds = self.testcase.setup
            if not isinstance(setup_cmds, list):
                setup_cmds = setup_cmds.splitlines()
            self.output("{}".format(setup_cmds))

            if ANSIBLE_NEW:
                # Ansible 2.2 and later:
                # Run setup_cmds regardless of current state.
                # In order to send a fixed list of commands as setup, we
                # must force the commands into the 'after' block, otherwise
                # the module removes duplicate lines, which may be needed
                # for the setup, e.g. setting shutdown on multiple interfaces:
                #       interface Loopback 1
                #       shutdown
                #       interface Loopback 2
                #       shutdown
                #       interface Loopback 3
                #       shutdown
                # If passed in as the 'lines', then what the module
                # ultimately sends is
                #       interface Loopback 1
                #       shutdown
                #       interface Loopback 2
                #       interface Loopback 3
                #
                # Another issue is that sometime an EOS configuration
                # session (result of command `configure session <id>`)
                # may get left behind by Ansible. If these accumulate,
                # we could end up maxing out our pending sessions. Setting
                # max pending to 1 and then to 10 accomplishes two things:
                # it clears all but 1 pending session, opening up 9 more
                # for use; it provides the required 'lines' values needed
                # to be able to send the 'after' commands.
                args = {
                    'module': 'eos_config',
                    'description': 'Run test case setup commands',
                    'lines': [
                        'service configuration session max pending 1',
                        'service configuration session max pending 10'
                    ],
                    'after': setup_cmds,
                    'match': 'none',
                }
            else:
                # Ansible 2.1
                args = {
                    'module': 'eos_command',
                    'description': 'Run test case setup commands',
                    'cmds': ['configure terminal'] + setup_cmds + ['exit'],
                }

            arguments = [json.dumps(args)]

            ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                                  arguments=arguments)

            if ret_code != 0:
                LOG.write("Playbook stdout:\n\n{}".format(out))
                LOG.write("Playbook stderr:\n\n{}".format(err))
                raise RuntimeError("Error in test case setup")

    def tearDown(self):
        if self.testcase.teardown:
            self.output('Running test case teardown commands')
            teardown_cmds = self.testcase.teardown
            if not isinstance(teardown_cmds, list):
                teardown_cmds = teardown_cmds.splitlines()
            self.output("{}\n".format(teardown_cmds))

            if ANSIBLE_NEW:
                # Ansible 2.2
                # Run teardown_commands regardless of current state
                args = {
                    'module': 'eos_config',
                    'description': 'Run test case teardown_cmds commands',
                    'lines': teardown_cmds,
                    'match': 'none',
                }
            else:
                # Ansible 2.1
                args = {
                    'module': 'eos_command',
                    'description': 'Run test case teardown_cmds commands',
                    'cmds': ['configure terminal'] + teardown_cmds,
                }

            arguments = [json.dumps(args)]

            ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                                  arguments=arguments)

            if ret_code != 0:
                self.output("Playbook stdout:\n\n{}".format(out))
                self.output("Playbook stderr:\n\n{}".format(err))
                warnings.warn("\nError in test case teardown\n\n{}".format(
                    out))

    @classmethod
    def output(cls, text):
        print '>>', str(text)
        LOG.write('++ {}'.format(text) + '\n')

    def format_config_list(self, config):
        # Format a configuration for Ansible version specific requirements

        # Because Ansible 2.2 and later use eos_config instead of
        # eos_template, we need to format a configuration string
        # for run_validation according to the Ansible version in use.
        # eos_template takes a string in EOS config format (three-space
        # indent). eos_config takes a dictionary with keys for the
        # 'lines' to be applied, and the 'parents' of those lines if
        # not top-level commands.

        if ANSIBLE_NEW:
            values = []
            # Use a regex to find the top-level lines and their
            # sub-level lines
            matches = re.findall(r'^(\S.*\n)((\s+.*\n)*)', config, re.M)
            if matches:
                for match in matches:
                    if match[1]:
                        # A top level entry with sub level lines
                        # Split the sub level lines an strip leading spaces
                        values.append({
                            'lines': [l.lstrip() for l in match[1].splitlines()],
                            'parents': [match[0].rstrip('\n')]
                        })
                    else:
                        # A single top level line
                        values.append({'lines': [match[0].rstrip('\n')]})
            else:
                self.output("format_config_list:\n\n{}".format(config))
                raise ValueError('Improperly formatted configuration sample '
                                 'could not be formatted for use')
            return values
        else:
            # Ansible 2.1 and earlier use eos_template, so we do
            # not need to reformat the string. Just return it in a list.
            return [config]

    def run_module(self):
        (retcode, out, _) = self.execute_module()
        out_stripped = re.sub(r'\"config\": \"! Command:.*\\nend\"',
                              '\"config\": \"--- stripped for space ---\"',
                              out)
        LOG.write("PLaybook stdout:\n\n{}".format(out_stripped))
        if (self.testcase.negative):
            # This is a negative testcase, look for a return code
            # other than 0
            msg = "Expected failure, return code: {}".format(retcode)
            self.output(msg)
            assert retcode != 0, msg
        else:
            # This is a positive testcase, expect return code 0
            msg = "Return code: {}, Expected code: 0".format(retcode)
            self.output(msg)
            assert retcode == 0, msg
        return self.parse_response(out)

    def execute_module(self):
        arguments = [json.dumps(self.testcase.arguments)]
        arguments.append(json.dumps(
            {'rolename': "ansible-eos-{}".format(ROLE)}))
        return ansible_playbook(EOS_ROLE_PLAYBOOK, arguments=arguments)

    def parse_response(self, output, validate=False):
        # Get all the lines after the 'PLAY RECAP ****...' header
        lines = re.sub(r'^.*PLAY RECAP \*+', '', output, 0, re.S).split('\n')
        # Remove any empty lines from the list
        lines = [x for x in lines if x]

        recap = []
        for line in lines:
            match = re.search(r'^(\S+)\s+\:\s+'
                              r'ok=(\d+)\s+'
                              r'changed=(\d+)\s+'
                              r'unreachable=(\d+)\s+'
                              r'failed=(\d+)', line)
            if not match:
                self.output("Playbook stdout:\n\n{}".format(output))
                raise ValueError("Unable to parse Ansible output for "
                                 "recap information")
            (name, okcount, changed, unreach, failed) = match.groups()
            recap.append({name: {'ok': okcount,
                                 'changed': changed,
                                 'unreachable': unreach,
                                 'failed': failed}})

        if not validate:
            return recap

        updates = []
        for device in recap:
            hostname = device.keys()[0]
            match = re.search(
                r'(?<!skipping: )\[%s\] => '
                r'((?:\{(?:(?!TASK \[).*\n)*\})|'
                r'(?:\{(?:(?!TASK \[).*)\}))' % hostname, output, re.M)
            if not match:
                self.output("Playbook stdout:\n\n{}".format(output))
                raise ValueError("Unable to parse Ansible output for "
                                 "result validation")
            result = json.loads(match.group(1))
            updates.append({hostname: result})

        return updates

    def run_validation(self, src, desc='Validate configuration'):
        if ANSIBLE_NEW:
            # Use eos_config when running Ansible 2.2 or later
            # src is a dictionary with keys 'lines' and (optionally) 'parents'
            args = {
                'module': 'eos_config',
                'description': desc,
                'match': 'line'
            }
            args.update(src)
        else:
            # Use eos_template when running Ansible 2.1 or earlier
            args = {'module': 'eos_template', 'description': desc, 'src': src}

        arguments = [json.dumps(args)]
        (ret_code, out, _) = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                              arguments=arguments,
                                              options=['--check'])
        LOG.write(out)
        assert ret_code == 0, "Validation playbook failed execution"
        return self.parse_response(out, validate=True)


def filter_modules(modules, filenames):
    if modules:
        modules = ['{0}.yml'.format(s) for s in modules.split(',')]
        return list(set(modules).intersection(filenames))
    return filenames


def setup():
    print >> sys.stderr, "Test Suite Setup:"

    get_version = "  Determining Ansible version in use ..."
    print >> sys.stderr, get_version
    LOG.write('++ {}\n'.format(get_version.strip()))
    # Call ansible-playbook with the --version flag and parse
    # the output for the version string
    _, out, err = ansible_playbook(None, None, ['--version'])
    match = re.match('ansible-playbook\s+((\d+\.)+\d+)', out, re.M)
    if match:
        version = match.group(1)
    else:
        LOG.write(">> ansible-playbook stdout:\n{}".format(out))
        LOG.write(">> ansible-playbook stderr:\n{}".format(err))
        raise RuntimeError('Could not determine Ansible version')
    show_version = "    Ansible version is {}".format(version)
    print >> sys.stderr, show_version
    LOG.write('-- {}\n'.format(show_version.strip()))
    # Set global value of ANSIBLE_NEW to True if
    # version string is 2.2.0.0 or greater
    global ANSIBLE_NEW
    ANSIBLE_NEW = parse_version(version) >= parse_version('2.2.0.0')
    # Save the Ansible version to be used globally
    global ANSIBLE_VERSION
    ANSIBLE_VERSION = version

    run_backup = "  Backing up running-config on nodes ..."
    print >> sys.stderr, run_backup
    LOG.write('++ {}\n'.format(run_backup.strip()))
    if ANSIBLE_NEW:
        # Ansible >= 2.2
        # Don't need to check running-config, it will always fail
        # (match = none)
        args = {
            'module': 'eos_config',
            'description': 'Back up running-config on node',
            'lines': [
                'copy running-config {}'.format(RUN_CONFIG_BACKUP)
            ],
            'match': 'none',
        }
    else:
        # Ansible 2.1
        args = {
            'module': 'eos_command',
            'description': 'Back up running-config on node',
            'cmds': [
                'configure terminal',
                'copy running-config {}'.format(RUN_CONFIG_BACKUP)
            ],
        }
    arguments = [json.dumps(args)]

    ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                          arguments=arguments)

    if ret_code != 0:
        LOG.write(">> ansible-playbook "
                  "{} stdout:\n{}".format(EOS_MODULE_PLAYBOOK, out))
        LOG.write(">> ansible-playbook "
                  "{} stddrr:\n{}".format(EOS_MODULE_PLAYBOOK, err))
        teardown()
        raise RuntimeError("Error in Test Suite Setup")

    run_backup = "  Backing up startup-config on nodes ..."
    print >> sys.stderr, run_backup
    LOG.write('++ {}\n'.format(run_backup.strip()))
    if ANSIBLE_NEW:
        # Ansible 2.2
        # Don't need to check running-config, it will always fail
        # (match = none)
        args = {
            'module': 'eos_config',
            'description': 'Back up startup-config on node',
            'lines': [
                'copy startup-config {}'.format(START_CONFIG_BACKUP)
            ],
            'match': 'none',
        }
    else:
        # Ansible 2.1
        args = {
            'module': 'eos_command',
            'description': 'Back up startup-config on node',
            'cmds': [
                'configure terminal',
                'copy startup-config {}'.format(START_CONFIG_BACKUP)
            ],
        }
    arguments = [json.dumps(args)]

    ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                          arguments=arguments)

    if ret_code != 0:
        LOG.write(">> ansible-playbook "
                  "{} stdout:\n{}".format(EOS_MODULE_PLAYBOOK, out))
        LOG.write(">> ansible-playbook "
                  "{} stddrr:\n{}".format(EOS_MODULE_PLAYBOOK, err))
        teardown()
        raise RuntimeError("Error in Test Suite Setup")

    print >> sys.stderr, "  Gathering test cases ..."

    modules = os.environ.get('ANSIBLE_ROLE_TEST_CASES')

    testcases_home = os.path.join(HERE, 'testcases')
    if not os.path.exists(testcases_home):
        print >> sys.stderr, "\n  ***** Testcase directory not found!! *****"
        teardown()
        raise RuntimeError(
            "Testcase path '{}' does not exist".format(testcases_home)
        )

    filenames = os.listdir(testcases_home)

    for module in filter_modules(modules, filenames):
        path = os.path.join(testcases_home, module)
        definition = yaml.load(open(path))

        defaults = definition.get('defaults', {})
        testcases = definition.get('testcases', [])
        if not testcases:
            print >> sys.stderr, ("\n  ***** No testcases defined in "
                                  "module {} *****\n".format(module))
        else:
            for testcase in definition.get('testcases', []):
                kwargs = defaults.copy()
                kwargs.update(testcase)
                TESTCASES.append(TestCase(**kwargs))

    print >> sys.stderr, "  Setup complete\n"


def teardown():
    print >> sys.stderr, "\nTest Suite Teardown:"

    no_teardown = os.environ.get('NO_ANSIBLE_ROLE_TEST_TEARDOWN')

    if no_teardown:
        print >> sys.stderr, ("{}\n"
                              "  Skipping test suite teardown due to "
                              "NO_ANSIBLE_ROLE_TEST_TEARDOWN\n"
                              "  To restore each device to pre-test state "
                              "execute the following commands\n"
                              "  - configure terminal\n"
                              "  - configure replace {}\n"
                              "  - delete {}\n"
                              "  - copy {} startup-config\n"
                              "  - delete {}\n"
                              "{}".format(SEPARATOR, RUN_CONFIG_BACKUP,
                                          RUN_CONFIG_BACKUP,
                                          START_CONFIG_BACKUP,
                                          START_CONFIG_BACKUP, SEPARATOR))
    else:
        # Restore the running-config on the nodes
        # ---------------------------------------
        restore_backup = "  Restoring running-config on nodes ..."
        print >> sys.stderr, restore_backup
        LOG.write('++ {}\n'.format(restore_backup.strip()))
        if ANSIBLE_NEW:
            # Ansible 2.2
            # Don't need to check running-config, it will always fail
            # (match = none)
            args = {
                'module': 'eos_config',
                'description': 'Restore running-config from backup',
                'lines': [
                    'configure replace {}'.format(RUN_CONFIG_BACKUP),
                    'delete {}'.format(RUN_CONFIG_BACKUP),
                ],
                'match': 'none',
            }
        else:
            # Ansible 2.1
            args = {
                'module': 'eos_command',
                'description': 'Restore running-config from backup',
                'cmds': [
                    'configure terminal',
                    'configure replace {}'.format(RUN_CONFIG_BACKUP),
                    'delete {}'.format(RUN_CONFIG_BACKUP),
                ],
            }
        arguments = [json.dumps(args)]

        # ret_code, out, err = ansible_playbook(CMD_PLAY, arguments=arguments)
        ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                              arguments=arguments)

        if ret_code != 0:
            msg = "Error restoring running-config on nodes\n" \
                  "Running ansible-playbook {} -e {}\n" \
                  ">> stdout: {}\n" \
                  ">> stderr: {}\n".format(EOS_MODULE_PLAYBOOK,
                                           arguments, out, err)
            warnings.warn(msg)

        # Restore the startup-config on the nodes
        # ---------------------------------------
        restore_backup = "  Restoring startup-config on nodes ..."
        print >> sys.stderr, restore_backup
        LOG.write('++ {}\n'.format(restore_backup.strip()))
        if ANSIBLE_NEW:
            # Ansible 2.2
            # Don't need to check running-config, it will always fail
            # (match = none)
            args = {
                'module': 'eos_config',
                'description': 'Restore startup-config from backup',
                'lines': [
                    'copy {} startup-config'.format(START_CONFIG_BACKUP),
                    'delete {}'.format(START_CONFIG_BACKUP),
                ],
                'match': 'none',
            }
        else:
            # Ansible 2.1
            args = {
                'module': 'eos_command',
                'description': 'Restore startup-config from backup',
                'cmds': [
                    'configure terminal',
                    'copy {} startup-config'.format(START_CONFIG_BACKUP),
                    'delete {}'.format(START_CONFIG_BACKUP),
                ],
            }
        arguments = [json.dumps(args)]

        # ret_code, out, err = ansible_playbook(CMD_PLAY, arguments=arguments)
        ret_code, out, err = ansible_playbook(EOS_MODULE_PLAYBOOK,
                                              arguments=arguments)

        if ret_code != 0:
            msg = "Error restoring startup-config on nodes\n" \
                  "Running ansible-playbook {} -e {}\n" \
                  ">> stdout: {}\n" \
                  ">> stderr: {}\n".format(EOS_MODULE_PLAYBOOK,
                                           arguments, out, err)
            warnings.warn(msg)

    print >> sys.stderr, "  Teardown complete"


def test_module():
    for testcase in TESTCASES:
        yield TestModule(testcase)


def ansible_playbook(playbook, arguments=None, options=None):
    if arguments is None:
        arguments = []
    if options is None:
        options = []

    command = ['ansible-playbook']

    if playbook:
        command.append(playbook)
    command.extend(['-i', INVENTORY])
    for arg in arguments:
        command.extend(['-e', arg])
    for opt in options:
        command.append(opt)
    command.append('-vvv')

    # Format the command string for output on error - for easier
    # copy/paste for manual run
    cmdstr = ''
    for segment in command:
        if segment[0] == '{':
            cmdstr = cmdstr + "\'{}\' ".format(segment)
        else:
            cmdstr = cmdstr + "{} ".format(segment)
    LOG.write("-- Ansible playbook command:\n-- {}\n".format(cmdstr))

    stdout = subprocess.PIPE
    stderr = subprocess.PIPE
    proc = subprocess.Popen(command, stdout=stdout, stderr=stderr)
    out, err = proc.communicate()

    return (proc.returncode, out, err)
