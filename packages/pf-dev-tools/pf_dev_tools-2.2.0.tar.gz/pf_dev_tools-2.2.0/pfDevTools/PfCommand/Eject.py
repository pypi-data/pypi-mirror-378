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
import time
import traceback

from typing import List
from sys import platform
from pathlib import Path

from PyUtilities import Utility
from PyUtilities.Exceptions import ArgumentError
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.PfCommand.Command import Command


# -- Classes
class Eject(Command):
    """A tool to eject given volume (SD card or Pocket in USB access mode)."""

    @classmethod
    def name(cls) -> str:
        return 'eject'

    @classmethod
    def usage(cls) -> None:
        print('   eject <dest_volume>                   - Eject volume.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 0:
            self._volume_path = CoreConfig.core_install_volume_path()
        elif nb_of_arguments == 1:
            self._volume_path = Path(arguments[0])
        else:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        try:
            if not self._volume_path.exists():
                raise RuntimeError(f'Volume {self._volume_path} is not mounted.')

            if platform == 'darwin':
                print(f'Ejecting {self._volume_path}.')
                Utility.shell_command(['diskutil', 'eject', f'{self._volume_path}'])

                while self._volume_path.exists():
                    time.sleep(1)

                print('Done.')
            elif platform == 'linux':
                if not Utility.command_exists('eject'):
                    raise RuntimeError('Cannot find "eject" command. Unable to eject volume.')

                print(f'Ejecting {self._volume_path}.')

                # noinspection PyBroadException
                try:
                    Utility.shell_command(['eject', str(self._volume_path)], capture_output=True)
                except Exception:
                    # -- Right now we get an error about the device but the volume is ejected
                    # -- so we will revisit this later.
                    pass

                while self._volume_path.exists():
                    time.sleep(1)

                print('Done.')
            elif platform == 'win32':
                if not Utility.command_exists('powershell'):
                    raise RuntimeError('Cannot find "eject" command. Unable to eject volume.')

                print(f'Ejecting {self._volume_path}.')
                Utility.shell_command(['powershell', '(New-Object -comObject Shell.Application).'
                                       f'Namespace(17).ParseName("{self._volume_path}").'
                                       'InvokeVerb("Eject");Start-Sleep -Seconds 3'], capture_output=True)

                while self._volume_path.exists():
                    time.sleep(1)
            else:
                print('Ejecting volumes is only supported on macOS, Linux and Windows right now.')
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while ejecting volume.')

            sys.exit(1)
