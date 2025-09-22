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
from pathlib import Path

from PyUtilities.Exceptions import ArgumentError
from pfDevTools.PfCommand.Command import Command


# -- Classes
class Reverse(Command):
    """A tool to reverse the bitstream of a rbf file for an Analog Pocket core."""

    @classmethod
    def name(cls) -> str:
        return 'reverse'

    @classmethod
    def usage(cls) -> None:
        print('   reverse src_filename dest_filename    - Reverse a bitstream file.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on

        if len(arguments) != 2:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._rbf_filename = Path(arguments[0])
        self._rbf_r_filename = Path(arguments[1])

        if self._rbf_filename.suffix != '.rbf':
            raise ArgumentError('Can only reverse .rbf files.')

        if not self._rbf_filename.exists():
            raise ArgumentError(f'File "{self._rbf_filename}" does not exist.')

    def run(self) -> None:
        try:
            print(f'Reading "{self._rbf_filename}".')
            input_file = open(self._rbf_filename, 'rb')
            input_data = input_file.read()
            input_file.close()

            reversed_data = []
            print(f'Reversing {len(input_data)} bytes.')
            for byte in input_data:
                reversed_byte = (((byte & 1) << 7) | ((byte & 2) << 5) | ((byte & 4) << 3) | ((byte & 8) << 1) |
                                 ((byte & 16) >> 1) | ((byte & 32) >> 3) | ((byte & 64) >> 5) | ((byte & 128) >> 7))
                reversed_data.append(reversed_byte)

            print(f'Writing "{self._rbf_r_filename}".')
            output_file = open(self._rbf_r_filename, 'wb')
            output_file.write(bytearray(reversed_data))
            output_file.close()
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while reversing bitstream.')

            sys.exit(1)
