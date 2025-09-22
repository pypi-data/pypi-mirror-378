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
import getopt
import semver

from typing import List, Optional

from PyUtilities import Utility, Git
from PyUtilities.Exceptions import ArgumentError
from pfDevTools.__about__ import __version__
from pfDevTools.Paths import Paths
from pfDevTools.PfCommand.Command import Command
from pfDevTools.PfCommand.Clean import Clean
from pfDevTools.PfCommand.Clone import Clone
from pfDevTools.PfCommand.Convert import Convert
from pfDevTools.PfCommand.Delete import Delete
from pfDevTools.PfCommand.DryRun import DryRun
from pfDevTools.PfCommand.Eject import Eject
from pfDevTools.PfCommand.Install import Install
from pfDevTools.PfCommand.Make import Make
from pfDevTools.PfCommand.Program import Program
from pfDevTools.PfCommand.Qfs import Qfs
from pfDevTools.PfCommand.Reverse import Reverse


# -- Classes
class PfCommand:
    """The pf command line tool for Project Freedom."""

    @classmethod
    def print_version(cls) -> None:
        print(f'👾 pf-dev-tools v{__version__} 👾')

        PfCommand.check_for_updates(force_check=True)

    @classmethod
    def check_for_updates(cls, force_check: bool = False) -> None:
        # noinspection PyBroadException
        try:
            file_path = Paths.app_update_check_file()
            if not force_check and not Utility.file_older_than(file_path, time_in_seconds=(24 * 60 * 60)):
                return

            latest_version = Git.Repo('code.malenfant.net/didier/pfDevTools').get_latest_version()
            if latest_version is None:
                return

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.unlink(missing_ok=True)

            with open(file_path, 'w') as out_file:
                out_file.write('check')

            if latest_version > semver.Version.parse(__version__):
                warning = '‼️' if sys.platform == "darwin" else '!!'
                print(f'{warning}  Version v{str(latest_version)} is available for pf-dev-tools. '
                      f'You have v{__version__} {warning}')
                print('Please run "pip install pf-dev-tools --upgrade" to upgrade.')
        except Exception:
            pass

    def __init__(self, args: List[str]):
        """Constructor based on command line arguments."""

        try:
            self._commands = [Clean, Clone, Convert, Delete, DryRun, Eject, Install, Make,
                              Program, Qfs, Reverse]
            self._debug_on = False

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhv', ['debug', 'help', 'version'])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    self._debug_on = True
                elif o in ('-h', '--help'):
                    self.print_usage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    PfCommand.print_version()
                    sys.exit(0)

            if len(arguments) == 0:
                raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

            self._command_found: Optional[type[Command]] = None
            for command in self._commands:
                if command.name() == arguments[0]:
                    self._command_found = command
                    break

            if self._command_found is None:
                raise ArgumentError(f'Unknown command "{arguments[0]}". Maybe start with `pf --help?')

            self._arguments = arguments[1:]

        except getopt.GetoptError:
            print('Unknown option. Maybe start with `pf --help?')
            sys.exit(0)

    def main(self) -> None:
        if self._command_found is not None:
            self._command_found(self._arguments, debug_on=self._debug_on).run()

        PfCommand.check_for_updates()

    def print_usage(self) -> None:
        PfCommand.print_version()
        print('')
        print('usage: pf <options> command <arguments>')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h                             - Show a help message.')
        print('   --version/-v                          - Display the app\'s version.')
        print('   --debug/-d                            - Enable extra debugging information.')
        print('')
        print('Supported commands are:')

        for command in self._commands:
            command.usage()

        print('')
