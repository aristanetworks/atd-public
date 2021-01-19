# Copyright (c) 2017, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import (absolute_import, division, print_function)

import re
import collections

from ansible import errors

__metaclass__ = type

def parse_config(config, indent=1):
    regexp = re.compile(r'^\s*(.+)$')
    line_re = re.compile(r'\S')
    invalid_re = re.compile(r'^(!|end)')

    ancestors = list()
    data = collections.OrderedDict()

    for line in config:
        text = str(line).strip()

        if not invalid_re.match(text):

            # handle top level commands
            if line_re.match(line):
                data[text] = collections.OrderedDict()
                ancestors = [text]

            # handle sub level commands
            else:
                match = regexp.match(line)
                if match:
                    line_indent = match.start(1)
                    level = int(line_indent / indent)

                    try:
                        ancestors[level] = text
                    except IndexError:
                        ancestors.append(text)

                    try:
                        child = data[ancestors[0]]
                        for a in ancestors[1:level]:
                            child = child[a]
                        child[text] = collections.OrderedDict()
                    except KeyError:
                        # FIXME deal with indent inconsistencies
                        if '_errors' not in data:
                            data['_errors'] = list()
                        data['_errors'].append((ancestors, text))

    return data


def config_block(value, ancestors, indent=1):
    config = parse_config(value.split('\n'), indent)
    try:
        for ancestor in ancestors.split('.'):
            config = config[ancestor]
        return config.keys()
    except KeyError:
        # raise errors.AnsibleFilterError('Config block not found for parent')
        return None


def re_findall(value, regex):
    return re.findall(regex, value, re.M)


def re_search(value, regex):
    return re.search(regex, value, re.M)


class FilterModule(object):

    def filters(self):
        return {
            'config_block': config_block,
            're_findall': re_findall,
            're_search': re_search,
        }
