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

from typing import List, Optional
from pathlib import Path

from PyUtilities import Utility, Git
from PyUtilities.Exceptions import ArgumentError
from pfDevTools.PfCommand.Command import Command


# -- Classes
class Clone(Command):
    """A tool to clone the core template."""

    @classmethod
    def name(cls) -> str:
        return 'clone'

    @classmethod
    def usage(cls) -> None:
        print('   clone <url> <tag=name> dest_folder    - Clone core template repo or repo at url optionally '
              'at a given tag/branch.')
        print('                                           (url defaults to pfCoreTemplate\'s repo if missing).')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on
        self._tag_name: Optional[str] = None
        self._url = 'code.malenfant.net/didier/pfCoreTemplate'

        destination_folder: Optional[Path] = None

        nb_of_arguments = len(arguments)
        while nb_of_arguments:
            if nb_of_arguments == 1:
                destination_folder = Path(arguments[0])
            elif arguments[0].startswith('tag='):
                self._tag_name = arguments[0][4:]
            else:
                self._url = arguments[0]

            nb_of_arguments -= 1
            arguments = arguments[1:]

        if destination_folder is None:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._destination_folder = destination_folder

    def run(self) -> None:
        try:
            if self._destination_folder.exists():
                raise RuntimeError(f'Folder "{self._destination_folder}" already exists.')

            print(f'Cloning core template in "{self._destination_folder}".')

            Git.Repo(self._url).clone_in(self._destination_folder, self._tag_name, shallow=True)

            git_folder = self._destination_folder / '.git'
            if git_folder.exists():
                Utility.delete_folder(git_folder, force_delete=True)
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while cloning repo.')

            sys.exit(1)
