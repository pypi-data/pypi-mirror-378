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
import zipfile
import tempfile
import traceback
import shutil

from pathlib import Path
from typing import List, Optional

from PyUtilities.Exceptions import ArgumentError
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.PfCommand.Command import Command
from pfDevTools.PfCommand.Eject import Eject


# -- Classes
class Install(Command):
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    @classmethod
    def _delete_file(cls, filepath: Path) -> None:
        filepath.unlink(missing_ok=True)

    @classmethod
    def name(cls) -> str:
        return 'install'

    @classmethod
    def usage(cls) -> None:
        print('   install <--no_build> <--eject>        - Build and install project core.')
        print('                                           (--no_build: disable build before installing)')
        print('   install <--eject> zip_file <volume_path>.')
        print('                                         - Install packaged core on volume at volume_path.')
        print('                                           (--eject: eject the volume if install is successful)')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on
        self._no_build = False
        self._eject_when_done = False

        volume_path: Optional[Path] = None
        zipped_file: Optional[Path] = None

        nb_of_arguments = len(arguments)
        while nb_of_arguments > 0 and ((arguments[0] == '--no_build') or (arguments[0] == '--eject')):
            if arguments[0] == '--no_build':
                self._no_build = True

                nb_of_arguments -= 1
                arguments = arguments[1:]
            elif arguments[0] == '--eject':
                self._eject_when_done = True

                nb_of_arguments -= 1
                arguments = arguments[1:]

        if nb_of_arguments != 0:
            if nb_of_arguments == 2:
                volume_path = Path(arguments[1])
                arguments = [arguments[0]]
                nb_of_arguments -= 1
            else:
                volume_path = CoreConfig.core_install_volume_path()

            if nb_of_arguments != 1:
                raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

            zipped_file = Path(arguments[0])

            if zipped_file.stem != '.zip':
                raise ArgumentError('Can only install zipped up core files.')

            if not zipped_file.exists():
                raise ArgumentError(f'File "{zipped_file}" does not exist.')

            if not volume_path.exists():
                raise ArgumentError(f'Volume "{volume_path}" is not mounted.')

        if volume_path is None:
            raise ArgumentError('Cannot find a volume to install on.')

        self._volume_path = volume_path

        if zipped_file is None:
            raise ArgumentError('Cannot find a zip file to install.')

        self._zipped_file = zipped_file

    def _dest_assets_folder(self) -> Path:
        return self._volume_path / 'Assets'

    def _dest_cores_folder(self) -> Path:
        return self._volume_path / 'Cores'

    def _dest_platforms_folder(self) -> Path:
        return self._volume_path / 'Platforms'

    def run(self) -> None:
        try:
            # -- In a temporary folder.
            with tempfile.TemporaryDirectory() as tmp_dir_as_string:
                tmp_dir = Path(tmp_dir_as_string)

                # -- Unzip the file.
                with zipfile.ZipFile(self._zipped_file, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)

                # -- Copy assets files
                assets_src_folder = tmp_dir / 'Assets'
                if assets_src_folder.exists():
                    print('Copying assets files...')

                    assets_dest_folder = self._dest_assets_folder()

                    if not assets_src_folder.exists():
                        raise RuntimeError(f'Cannot find "{assets_src_folder}" in the core release zip file.')

                    shutil.copytree(assets_src_folder, assets_dest_folder)

                # -- Copy core files
                print('Copying core files...')

                core_src_folder = tmp_dir / 'Cores'
                core_dest_folder = self._dest_cores_folder()

                if not core_src_folder.is_dir():
                    raise RuntimeError(f'Cannot find "{core_src_folder}" in the core release zip file.')

                shutil.copytree(core_src_folder, core_dest_folder)

                # -- Copy platform files
                print('Copying platforms files...')

                platforms_src_folder = tmp_dir / 'Platforms'
                platforms_dest_folder = self._dest_platforms_folder()

                if not platforms_src_folder.is_dir():
                    raise RuntimeError(f'Cannot find "{platforms_src_folder}" in the core release zip file.')

                shutil.copytree(platforms_src_folder, platforms_dest_folder)
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while installing core.')

            sys.exit(1)

        if self._eject_when_done:
            Eject([], debug_on=self._debug_on).run()
