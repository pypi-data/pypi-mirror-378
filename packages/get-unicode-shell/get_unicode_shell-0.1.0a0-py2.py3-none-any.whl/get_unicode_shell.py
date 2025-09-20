# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from posix_or_nt import posix_or_nt
from read_unicode_environment_variables_dictionary import read_unicode_environment_variables_dictionary
from typing import Text


def get_unicode_shell():
    # type: () -> Text
    unicode_environment_variables_dictionary = read_unicode_environment_variables_dictionary()
    if posix_or_nt() == 'nt':
        comspec_or_none = unicode_environment_variables_dictionary.get(u'COMSPEC', None)
        if comspec_or_none is not None:
            return comspec_or_none
        else:
            return u'cmd.exe'
    else:
        shell_or_none = unicode_environment_variables_dictionary.get(u'SHELL', None)
        if shell_or_none is not None:
            return shell_or_none
        else:
            return u'/bin/sh'
