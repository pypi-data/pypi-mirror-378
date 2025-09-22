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
import shutil
import traceback

from typing import List
from pathlib import Path

from PyUtilities.Exceptions import ArgumentError
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.PfCommand.Command import Command


# -- Classes
class Delete(Command):
    """A tool to delete a core from a given volume (SD card or Pocket in USB access mode)."""

    @classmethod
    def _delete_file(cls, file: Path) -> None:
        file.unlink(missing_ok=True)

    @classmethod
    def _core_name_from(cls, name: Path) -> str:
        extension = name.suffix
        if len(extension) > 1:
            extension = extension[1:]

        return extension

    @classmethod
    def name(cls) -> str:
        return 'delete'

    @classmethod
    def usage(cls) -> None:
        print('   delete core_name <dest_volume>        - Delete core on volume.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 2:
            self._volume_path = Path(arguments[1])
            arguments = arguments[:0]
            nb_of_arguments -= 1
        else:
            self._volume_path = CoreConfig.core_install_volume_path()

        if len(arguments) != 1:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._name_of_core_to_delete = Path(arguments[0])

    def _dest_cores_folder(self) -> Path:
        return self._volume_path / 'Cores'

    def _dest_platforms_folder(self) -> Path:
        return self._volume_path / 'Platforms'

    def run(self) -> None:
        try:
            cores_folder = self._dest_cores_folder()
            core_folder = cores_folder / self._name_of_core_to_delete

            if core_folder.exists():
                print(f'Deleting "{core_folder}"...')
                shutil.rmtree(core_folder, ignore_errors=True)

            hidden_core_data = self._dest_cores_folder() / '._' / self._name_of_core_to_delete
            if hidden_core_data.exists():
                print(f'Deleting "{hidden_core_data}"...')
                Delete._delete_file(hidden_core_data)

            core_name = Delete._core_name_from(self._name_of_core_to_delete)
            if len(core_name) == 0:
                raise RuntimeError(f'Could not figure out the core name from "{self._name_of_core_to_delete}".')

            for p in Path(cores_folder).rglob('*'):
                if not p.is_dir():
                    continue

                if Delete._core_name_from(p) == core_name:
                    print(f'Found another implementation of the {core_name} '
                          'platform, not deleting any Platform data for this core.')
                    return

            platforms_folder = self._dest_platforms_folder()
            core_name = core_name.lower()
            for p in Path(platforms_folder).rglob('*'):
                core_found = Path(p)
                if core_found.is_dir():
                    continue

                filename = core_found.name
                if filename == f'{core_name}.bin':
                    print(f'Deleting "{str(p)}"...')
                    self._delete_file(p)
                elif filename == f'{core_name}.json':
                    print(f'Deleting "{str(p)}"...')
                    self._delete_file(p)
                elif filename == f'._{core_name}.bin':
                    print(f'Deleting "{str(p)}"...')
                    self._delete_file(p)
                elif filename == f'._{core_name}.json':
                    print(f'Deleting "{str(p)}"...')
                    self._delete_file(p)
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while deleting core.')

            sys.exit(1)
