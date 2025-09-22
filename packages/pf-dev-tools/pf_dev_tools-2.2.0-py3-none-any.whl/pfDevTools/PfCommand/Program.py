#
# Copyright (c) 2023-present Didier Malenfant
#
# This file is part of pfDevTools.
#
# pfDevTools is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pfDevTools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with pfDevTools. If not,
# see <https://www.gnu.org/licenses/>.
#

import sys
import traceback

from typing import List

from PyUtilities import Utility
from PyUtilities.Exceptions import ArgumentError
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.PfCommand.Command import Command


# -- Classes
class Program(Command):
    """A tool to program the Analogue Pocket via JTAG."""

    @classmethod
    def name(cls) -> str:
        return 'program'

    @classmethod
    def usage(cls) -> None:
        print('   program                               - Build and program the Analogue Pocket.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on

        if len(arguments) > 0:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._volume_path = CoreConfig.core_install_volume_path()

    def run(self) -> None:
        try:
            command_line = ['scons', '-Q', '-s', 'program']

            if self._debug_on:
                command_line.append('--debug_on')

            Utility.shell_command(command_line)

        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while programming Pocket.')

            sys.exit(1)
