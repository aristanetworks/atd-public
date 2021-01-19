
Arista Roles for Ansible - Development Guidelines
=================================================

#### Table of Contents

* [Executing Test Cases for an Arista Ansible Role] (#executing-test-cases-for-an-arista-ansible-role)
  * [Overview] (#overview)
  * [Details] (#details)
* [Developing Arista Roles For Ansible] (#developing-arista-roles-for-ansible)
  * [Preparing the Role Development Workspace] (#preparing-the-role-development-workspace)
    * [Existing Role Development] (#existing-role-development)
    * [New Arista Ansible role development] (#new-arista-ansible-role-development)
  * [Role Development Guidelines] (#role-development-guidelines)
    * [Define the role's task list] (#define-the-roles-task-list)
    * [Implement jinja2 templates for the role's tasks] (#implement-jinja2-templates-for-the-roles-tasks)
    * [Include supporting files and documentation] (#include-supporting-files-and-documentation)
  * [Role Test Development] (#role-test-development)  
  * [Development for arista-ansible-role-test] (#development-for-arista-ansible-role-test)



Executing Test Cases for an Arista Ansible Role
-----------------------------------------------

#### Overview

To execute a role test suite:

- Update test/fixtures/hosts with the name(s) of your test devices.
- Update test/arista-ansible-role-test/group_vars/all.yml with the
  connection information for your devices.
- Execute `make tests` from the root of the role directory.

#### Details

This test framework should be used in a cloned copy of an Arista
ansible-eos-* Ansible role. The framework will ***not*** execute properly in an
ansible-galaxy installation of the role.

The arista-ansible-role-test framework is included as a subtree within
the Arista role. The framework is maintained in a separate repo located
at https://github.com/arista-eosplus/arista-ansible-role-test.

To use the test framework in your local environment, you will first need
to update test/fixtures/hosts and test/arista-ansible-role-test/group_vars/all.yml.
The hosts file should list your testing devices under the [test_hosts] 
section. The all.yml file should reflect the proper connection
parameters for your devices under the provider mapping.

Once the files have been updated for your local environment, execute
`make tests` from the root of the role directory to run the test suite against
the role.

To run a specific set of tests from the test suite, set the environment
variable `ANSIBLE_ROLE_TEST_CASES` to the name(s) of the file(s) under
test/testcases that you wish to execute (excluding the yml extension).
For example, if the testcases folder contains test files named first.yml,
second.yml, and third.yml, setting `ANSIBLE_ROLE_TEST_CASES=first,third`
would run only the tests in first.yml and third.yml.

The test framework executes the following steps when processing a test suite:
- The current state of each device is backed up in the /mnt/flash directory
  on the device using the `copy running-config <backup_file>` command.
- The current startup-config for each device is also backed up.
- Test cases are gathered from every file under test/testcases that matches
  the `ANSIBLE_ROLE_TEST_CASES` pattern, or all files if the variable is unset.
- Each test case is executed:
  - Setup for the test case is performed, if any exists.
  - The test case is executed against the role, verifying idempotency and
    any present or absent configuration that should exist on the device.
  - Test case teardown is performed, if any exists.
- The configuration for each device is restored from the backup file
  generated at test initialization.
- The startup-config for each device is restored from its backup location.
- The backup files are removed from each device, leaving the device in the
  state in which it was before the tests.

To prevent restoring device configuration after tests have run (to debug
a failing test case, for example), set the environment variable
`NO_ANSIBLE_ROLE_TEST_TEARDOWN` to True (or any value that would evaluate to true).
In this case, restoring the device configuration may be accomplished manually
by issuing the commands `configure replace <backup_file>` and
`copy <backup_of_startup> startup-config` on each device. A
message should have been printed in the test output indicating the file names
used for the backups, as well as how to restore the device and delete the backups.


Developing Arista roles for Ansible
-----------------------------------

#### Preparing the Role Development Workspace

##### Existing role development

To begin development on an existing Arista Ansible role, clone/fork
the role repository to your working environment, create a working 
branch, and proceed with development.

##### New Arista Ansible role development

To begin development on a new Arista role for Ansible, initialize a 
role directory using the `ansible-galaxy init` command.
  ```
  ansible-galaxy init ansible-eos-newrole
  ```

This will create a directory named ansible-eos-newrole with the following
directory structure:
  ```
    README.md
    .travis.yml
    defaults/
      main.yml
    files/
    handlers/
      main.yml
    meta/
      main.yml
    templates/
    tests/
      inventory
      test.yml
    vars/
      main.yml
  ```

Remove the .travis.yml file and the tests/ directory.

From an existing Arista role, copy the following files into the new
role's path, creating any missing directories as needed, and updating
file information to match the new role:

- .gitignore
- Makefile*
  - files/README.md
  - filter_plugins/config_block.py
  - handlers/main.yml
  - meta/main.yml*
  - test/fixtures/hosts


```
Note: An asterisk (*) indicates copied file should be reviewed for changes
specific to the new role, such as updating the role name.
```

#### Role development guidelines

An Arista role for Ansible consists of a list of tasks (tasks/main.yml) and
associated jinja2 templates (templates/*.j2) that will process a set of host
variables defined in an Ansible host_vars file.

The development of an Arista role for Ansible includes defining the set of 
tasks for the role, implementing the jinja2 templates for each of the
role-specific tasks, and providing any supporting files and documentation for
the role.

##### Define the role's task list

The task list for the role is defined in tasks/main.yml.

Every Arista role should contain two tasks at the top of the list which will
gather the current running-config from the device and store it in the variable
`_eos_config`. 

  ```
  - name: Gather EOS configuration
    eos_command:
      commands: 'show running-config all | exclude \.\*'
      provider: "{{ provider | default(omit) }}"
      auth_pass: "{{ auth_pass | default(omit) }}"
      authorize: "{{ authorize | default(omit) }}"
      host: "{{ host | default(omit) }}"
      password: "{{ password | default(omit) }}"
      port: "{{ port | default(omit) }}"
      transport: "cli"
      use_ssl: "{{ use_ssl | default(omit) }}"
      username: "{{ username | default(omit) }}"
    register: output
    no_log: "{{ no_log | default(true) }}"
    when: _eos_config is not defined

  - name: Save EOS configuration
    set_fact:
      _eos_config: "{{ output.stdout[0] }}"
    no_log: "{{ no_log | default(true) }}"
    when: _eos_config is not defined
  ```

Then call each task that will be defined for the role itself, using the 
following format:

  ```
    - name: Arista EOS < XXX task description >
      eos_template:
        src: XXXtemplatenameXXX.j2
        include_defaults: true
        config: "{{ _eos_config | default(omit) }}"
        auth_pass: "{{ auth_pass | default(omit) }}"
        authorize: "{{ authorize | default(omit) }}"
        host: "{{ host | default(omit) }}"
        password: "{{ password | default(omit) }}"
        port: "{{ port | default(omit) }}"
        provider: "{{ provider | default(omit) }}"
        transport: 'cli'
        use_ssl: "{{ use_ssl | default(omit) }}"
        username: "{{ username | default(omit) }}"
      notify: save running config
  ```

Refer to existing Arista roles and the Ansible documentation for examples on
using when, with_items, and other conditional statements to refine the 
execution of the tasks in the role.

Occasionally, a task may result in a change that needs to be propagated to the
stored _eos_config (tasks affect the running-config, not the stored _eos_config).
This may occur when an individual task produces results that are necessary may
not be in the initial configuration, but have updated the running-config. In 
this instance, a block statement may be used to update the stored configuration
if a change has occurred. Refer to an existing Arista role, such as 
ansible-eos-vxlan, for an example of how this might be handled.

##### Implement jinja2 templates for the role's tasks

Each task in the role's task list (other than those tasks for retrieving and
storing the running-config) should have a jinja2 file listed as the src entry
(XXXtemplatenameXXX.j2 in the example above). The jinja2 template files
take information from the passed in host_var definition and convert those to
a set of configuration entries that match those lines as they would be 
returned from a `show running-config all` command on EOS.

So, for example, a template that would set the hostname on the device would 
return the following line. 

  ```
  hostname <newhostname>
  ```

A template that would configure elements of a BGP setup would require indented
information in addition to the initial `router bgp` call.

  ```
  router bgp 113
     no shutdown
     router-id 13.13.13.13
     maximum-paths 3 ecmp 14
  ```

Note that indented lines must match the three-space indentation exactly as is
returned by the EOS configuration output. The information returned from the 
template is matched to the stored configuration to determine what calls will
be sent to the device.

To maintain consistency, please follow the following formatting guidelines
for jinja2 templates included with Arista roles.


  * Each template should contain the file name marker, and set trim_blocks and
    lstrip_blocks to false at the top of the file
  * Indentation should be 3 spaces for all lines in the file
  * Jinja filter pipes should be surrounded by a single space
  * Output lines from the template (the lines that will be returned and 
    compared with the stored config) should be preceeded and followed by
    a single blank line
    * Multiple sequential output lines may be grouped and the entire
      group enclosed by the single blank lines
  * Comments that span multiple lines should have each line begin with 
    the Jinja2 comment delimiter
    * The closing comment delimiter is only required on the last line
      of the multi-line comment
  * Comments should be used liberally to provide clarification to 
    the process taking place in the template
    * Mark the end of for loops and if blocks where useful
    * Explain the purpose of filters being used or sections of code


Below is a short example of the formatting for a template file. Refer to 
existing Arista roles template files for additional examples.

  ```
  ! templates/XXXtest.j2
  #jinja2: trim_blocks: False
  #jinja2: lstrip_blocks: False

  {% set state = item.state | default(eos_XXX_default_state) %}
  {% set name = item.name %}

  {# add a comment that spans several lines to keep the formatting
  {# and indentation across the multiple lines, making sure to close
  {# the comment after the final line #}

  {# set the netaddr by filtering through ipsubnet. note the space around the pipe #}
  {% set netaddr = srcaddr | ipsubnet(srcprefixlen) %}

  {% if not netaddr %}
     {# if srcprefixlen is 32, netaddr is False, so define the netaddr as a host IP #}
     {% set netaddr = "host %s" % srcaddr %}
  {% endif %}

  {# set the seqno and log strings to be used in the actual rule #}
  {% set seqno_rule = "%s " % seqno if seqno else '' %}
  {% set log_rule = ' log' if log else '' %}

  {# build the rule command line #}
  {% set rule = "%s%s %s%s" % (seqno_rule, action, netaddr, log_rule) %}
  
  {# send the rule - surround the output by blank lines #}
  
  {{ rule }}
  
  {# the comments around the output lines are not required, but are
  {# for the example only #}
  
  {# make sure the indentation is correct for an EOS configuration #}
  
  {% if something %}
     {% if x == y %}
     
  hostname {{ x }}    <-- note the indentation
  
     {% else %}
     
  hostname {{ abc }}
  
     {% endif %} {# x == y #}
  {% endif %} {# something #}
  ```

##### Include supporting files and documentation

Occasionally, a default value is desired for a variable within an Arista role,
as in the `set state` line in the example above. These defaults may be set 
in the defaults/main.yml file, and should be explanatory in their naming. 
Default values do not fill in missing host_vars values automatically, but must
be pulled in through a default filter as shown in the example.

There may also arise the need to implement a specific filter to be used by the
role. Filters are written in python and located in the filter_plugins 
directory. The config_block filter is included in all roles, and contains
filters to return a block of configuration from the _eos_config file, as well
as regular expression search and findall filters for matching lines in the
config. Additional filters may be implemented as necessary. See the range filter
in ansible-eos-mlag for an example.

Finally, make sure the README.md is properly updated for the role. Include a
brief description of the purpose of the role, role variable information, any
dependencies, and an example playbook. Refer to existing Arista roles for
content examples, and sections that may be copied and pasted for ease.


#### Role test development

* Make sure the role's README.md file includes the **Developer Information**
  section, which points to this document under the role's 
  test/arista-ansible-role-test directory. This information can be copied from
  an existing role's README file.

* Create a testcases directory for the role:

    ```
    --roletest-- >> mkdir -p test/testcases/
    ```

* Import the arista-ansible-role-test repository into the role as a subtree.
  From the root of the role directory, issue the following commands:
  * git remote add role-test https[]()://github.com/arista-eosplus/arista-ansible-role-test.git  
  * git subtree add --prefix=test/arista-ansible-role-test --squash role-test master  


      ```
      NOTE: These commands must be issued from a clean repo branch without any
      pending changes or commits. The `git subtree add` command will generate
      a commit to add the external repo to the working repository.
      
      --roletest-- >> git remote add role-test https://github.com/arista-eosplus/arista-ansible-role-test.git  
      --roletest-- >> git subtree add --prefix=test/arista-ansible-role-test --squash role-test master  
      git fetch role-test master  
      warning: no common commits  
      remote: Counting objects: 59, done.  
      remote: Compressing objects: 100% (24/24), done.  
      remote: Total 59 (delta 14), reused 0 (delta 0), pack-reused 35  
      Unpacking objects: 100% (59/59), done.  
      From https://github.com/arista-eosplus/arista-ansible-role-test  
      * branch            master     -> FETCH_HEAD  
      * [new branch]      master     -> role-test/master  
      Added dir 'test/arista-ansible-role-test'  
      ```

* Add test cases for the role:

  Create a yml file for each group of test cases under the test/testcases
  directory. Each group test file name should reflect the type of tests being
  run in that group. When a role contains several template modules, it is a
  good idea to have at least one test group for each template. Templates that
  perform multiple configuration changes may also be separated into several
  test group files.

  Each test group file must contain the ``defaults`` and ``testcases`` key words
  described below.

  **defaults** (dictionary) containing the following key:

  |    Key | Type              | Notes                                    |
  | -----: | ----------------- | ---------------------------------------- |
  | module | string (required) | The name of the test case file, without the .yml extension. This is used within the test framework to display the current test group information in the test suite output. |

  **testcases** (list) each entry contains the following keys:

  |       Key | Type                | Indentation | Notes                                    |
  | --------: | ------------------- | :---------: | ---------------------------------------- |
  |      name | string (required)   |     n/a     | The name of the test case, usually a brief description, such as "Modify and purge bgp neighbors" |
  | arguments | list (required)     |     n/a     | The role-specific arguments that will be used within the test case. |
  |     setup | yaml string literal |     no      | A list of setup commands to be run on each device before executing the test case. These setup commands are specific to one individual test case. This would be a list of commands as you would type them at the device console, without indentation. |
  |  teardown | yaml string literal |     no      | A list of commands that will be run on each device after the test case is executed. These commands are specific to one individual test case. This is a list of commands as you would type them at the device console, without indentation |
  |   present | yaml string literal |     yes     | A list of configuration entries that are expected to exist on the device after the the test case has executed the Ansible role. This list of configuration entries must be properly indented for matching against the current running-config on the device. |
  |    absent | yaml string literal |     yes     | A list of configuration entries that are expected to not exist on the device after the test case has executed the Ansible role. This list of configuration entries must be properly indented for matching against the current running-config on the device. |

  ```
  NOTES:
  * Test case examples are best seen by referring to the existing Arist roles
    and their included testcase files.
  * The yml string literal type used for the testcases 'setup', 'teardown',
    'present', and 'absent' keys is given by the pipe character immediately
    following the key, and no quotes are necessary:
       
        setup: |
          no vlan 1003
          vlan 1003
          name initial vlan 1003
          state suspend
        present: |
          vlan 1003
             name vlan 1003 changed
             state active
        absent: |
          vlan 1003
             name initial vlan 1003
             state suspend
             
  * Absent configurations may contain block headers that are present on the
    device, with block content that should not exist. In the sample above,
    the configuration block 'vlan 1003' is expected to exist on the device,
    but the state and name of the vlan has changed, so the lines
    'name initial vlan 1003' and 'state suspend' should not be present.
    
  ```

#### Development for arista-ansible-role-test

Because the arista-ansible-role-test framework repository has been included
as a subtree, direct modification of the test framework files is possible.
If you need to make changes to the framework itself, please follow the steps
outlined below, to make the propagation of the changes to the main 
framework repo as smooth as possible.

For the purposes of the instructions below, `role repo` refers to the base 
repository of the role you are working on (e.g. ansible-eos-vxlan), and
`framework repo` refers to the arista-ansible-role-test repository that was
imported as a subtree, i.e. everything under the /test/arista-ansible-role-test
directory in the role repo.

* Always make sure you have the latest changes for the framework repo
  in your local repository by issuing the command at the root of your role repo.

    ```
    git subtree pull --prefix=test/arista-ansible-role-test --squash role-test master
    ```

* Please keep commits to files in the framework directory 
  (test/arista-ansible-role-test) separate from commits to the rest of the role
  repo. This helps keep commit messages specific to the framework repo itself.
* Changes to the framework files must be committed to the role repo
  before being pushed to the framework repo. (git commit the framework 
  changes as part of the role repo before pushing the changes to the
  framework repo) 
* To push the changes to the framework repo, enter the following command
  at the root of the role repo, where `<branch>` is the name of a branch on
  the framework repo where the changes will be pushed. This branch will be
  created if it does not exist.

    ```
    git remote add role-test https://github.com/arista-eosplus/arista-ansible-role-test.git
    git subtree push --prefix=test/arista-ansible-role-test --squash role-test <branch>
    ```
    
* Make a pull request for the framework repo changes by visiting the
  [framework repo website] (https://github.com/arista-eosplus/arista-ansible-role-test.git).
  There you may create a new pull request for the branch created when you
  pushed the changes to the framework repo.



License
-------

Copyright (c) 2016, Arista Networks EOS+
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of Arista nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Author Information
------------------

Please raise any issues using our GitHub repo or email us at ansible-dev@arista.com
