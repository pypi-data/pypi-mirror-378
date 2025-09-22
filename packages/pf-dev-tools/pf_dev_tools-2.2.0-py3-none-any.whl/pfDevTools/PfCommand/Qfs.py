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
import tempfile
import shutil
import filecmp
import traceback

from typing import List, Optional
from enum import Enum
from pathlib import Path
from io import TextIOWrapper

from PyUtilities.Exceptions import ArgumentError
from pfDevTools.PfCommand.Command import Command


# -- Classes
class EditingState(Enum):
    BEFORE_EDIT = 1
    DURING_EDIT = 2
    AFTER_EDIT = 3


class Qfs(Command):
    """A tool to edit Quartus project files."""

    @classmethod
    def name(cls) -> str:
        return 'qfs'

    @classmethod
    def usage(cls) -> None:
        print('   qfs qsf_file <cpus=num> <optim=level> files')
        print('                                         - Add files to the project and set number of cpu '
              'or optimization level.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        super().__init__(arguments, debug_on)

        self._debug_on = debug_on

        nb_of_arguments = len(arguments)
        if nb_of_arguments < 3:
            raise ArgumentError('Invalid arguments. Maybe start with "pf --help"?')

        self._qsf_filename = Path(arguments[0])
        if self._qsf_filename.suffix != '.qsf':
            raise ArgumentError('Invalid input project file type for pf qsf.')

        if not self._qsf_filename.exists():
            raise ArgumentError(f'File "{self._qsf_filename}" does not exist.')

        arguments = arguments[1:]

        self._number_of_cpus: Optional[str] = None
        self._performance_optimizations = False

        while True:
            if arguments[0].startswith('cpus='):
                self._number_of_cpus = arguments[0][5:]
            elif arguments[0].startswith('optim='):
                level: str = arguments[0][6:]

                if level == 'none':
                    self._performance_optimizations = False
                elif level == 'perf':
                    self._performance_optimizations = True
                else:
                    raise ArgumentError(f'Invalid arguments "{level}" to "optim". Maybe start with "pf --help"?')
            else:
                break

            arguments = arguments[1:]

        self._verilog_files: List[str] = arguments

    def _write_additions(self, dest_file: TextIOWrapper, editing_wrappers: List[str]) -> None:
        dest_file.write(editing_wrappers[0])
        dest_file.write('# ---------------------------\n')

        if self._number_of_cpus is not None:
            dest_file.write(f'set_global_assignment -name NUM_PARALLEL_PROCESSORS {self._number_of_cpus}\n')

        if self._performance_optimizations:
            dest_file.write('set_global_assignment -name OPTIMIZATION_MODE "HIGH PERFORMANCE EFFORT"\n')
        else:
            dest_file.write('set_global_assignment -name OPTIMIZATION_MODE "BALANCED"\n')

        found_a_system_verilog_file: bool = False

        for file in self._verilog_files:
            dest_file.write('set_global_assignment -name ')

            if file.endswith('.v'):
                dest_file.write('VERILOG_FILE ')
            elif file.endswith('.sv'):
                dest_file.write('SYSTEMVERILOG_FILE ')

                found_a_system_verilog_file = True
            else:
                raise ArgumentError(f'Unknown file type for "{file}".')

            dest_file.write(file.replace('\\', '/') + '\n')

        if found_a_system_verilog_file:
            dest_file.write('set_global_assignment -name VERILOG_INPUT_VERSION SYSTEMVERILOG_2005\n')

        dest_file.write(f'\n{editing_wrappers[1]}')

    def run(self) -> None:
        try:
            editing_wrappers: List[str] = ['# Additions made by pf command\n',
                                           '# End of additions made by pf command\n']

            src_file = open(self._qsf_filename, 'r')

            # -- In a temporary folder.
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_file = Path(tmp_dir) / 'temp.qsf'
                dest_file = open(tmp_file, 'w')

                editing_state = EditingState.BEFORE_EDIT
                last_line = ''

                for line in src_file.readlines():
                    last_line = line

                    match editing_state:
                        case EditingState.BEFORE_EDIT:
                            if line == editing_wrappers[0]:
                                self._write_additions(dest_file, editing_wrappers)

                                editing_state = EditingState.DURING_EDIT
                            else:
                                dest_file.write(line)
                        case EditingState.DURING_EDIT:
                            if line == editing_wrappers[1]:
                                editing_state = EditingState.AFTER_EDIT
                        case EditingState.AFTER_EDIT:
                            dest_file.write(line)

                if editing_state == EditingState.BEFORE_EDIT:
                    if not last_line.endswith('\n'):
                        dest_file.write('\n')

                    if last_line != '\n':
                        dest_file.write('\n')

                    self._write_additions(dest_file, editing_wrappers)

                src_file.close()
                dest_file.close()

                if not filecmp.cmp(tmp_file, self._qsf_filename):
                    print('Updating QSF file...')
                    shutil.copyfile(tmp_file, self._qsf_filename)
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while editing QFS file.')

            sys.exit(1)
