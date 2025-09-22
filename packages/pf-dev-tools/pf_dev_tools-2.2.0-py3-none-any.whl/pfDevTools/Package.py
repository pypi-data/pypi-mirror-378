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

import os
import io
import sys
import shutil
import zipfile
import traceback

from typing import List, Optional
from pathlib import Path
from datetime import date

from PyUtilities.Exceptions import ArgumentError
from pfDevTools.PfCommand.Convert import Convert
from pfDevTools.PfCommand.Reverse import Reverse
from pfDevTools.CoreConfig import CoreConfig


# -- Classes
class Package:
    """A tool to package an analog pocket core"""

    @classmethod
    def _write_string_entry_from_value(cls, file: io.TextIOBase, entry_name: str, value: Optional[str],
                                       end_comma: bool = True, extra_spaces: str = '') -> None:
        if value is None:
            return

        string_version = f'"{value}"' if value.startswith('0x') else value
        comma_string = ',' if end_comma else ''

        file.write(f'        {extra_spaces}"{entry_name}": {string_version}{comma_string}\n')

    @classmethod
    def _write_boolean_entry_from_value(cls, file: io.TextIOBase, entry_name: str, value: Optional[bool],
                                        end_comma: bool = True, extra_spaces: str = '') -> None:
        if value is None:
            return

        string_version = "true" if value else "false"
        comma_string = ',' if end_comma else ''

        file.write(f'        {extra_spaces}"{entry_name}": {string_version}{comma_string}\n')

    def __init__(self, arguments: List[Path], debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on = debug_on

        if len(arguments) != 3:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._config = CoreConfig(arguments[0])
        self._destination_folder = arguments[1]
        self._packaging_folder = self._destination_folder / '_core'
        self._assets_folder = (self._packaging_folder / 'Assets' / self._config.platform_short_name() /
                               self._config.full_platform_name())
        self._cores_folder = self._packaging_folder / 'Cores' / self._config.full_platform_name()
        self._platforms_folder = self._packaging_folder / 'Platforms'
        self._platforms_images_folder = self._platforms_folder / '_images'

        self._today = str(date.today())
        if len(self._today) > 10:
            raise ArgumentError(f'Internal error generating today\'s date "{self._today}". '
                                f'Maximum length is 10 characters.')

        self._bitstream_files: List[List[Path]] = []
        for core_id in self._config.cores_list():
            self._bitstream_files.append([arguments[2] / self._config.core_source_file(core_id) /
                                          self._config.core_filename(core_id)])

    def _generate_data_file(self) -> None:
        with open(self._cores_folder / 'data.json', 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "data": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "data_slots": [')

            found_a_slot: bool = False
            for slot_id in self._config.file_slot_list():
                if found_a_slot:
                    out_file.write(',')

                out_file.write('\n      {\n')
                out_file.write(f'        "name": "{self._config.file_slot_name(slot_id)}",\n')
                out_file.write(f'        "id": {slot_id},\n')
                Package._write_boolean_entry_from_value(out_file, 'required',
                                                        self._config.file_slot_required(slot_id))
                out_file.write(f'        "parameters": {self._config.file_slot_parameters(slot_id)},\n')

                Package._write_boolean_entry_from_value(out_file, 'deferload',
                                                        self._config.file_slot_defer_loading(slot_id))
                Package._write_boolean_entry_from_value(out_file, 'secondary',
                                                        self._config.file_slot_secondary(slot_id))
                Package._write_boolean_entry_from_value(out_file, 'nonvolatile',
                                                        self._config.file_slot_non_volatile(slot_id))

                extensions: List[str] = self._config.file_slot_extensions(slot_id)
                if len(extensions) != 0:
                    out_file.write('        "extensions": [\n')
                    for extension in extensions:
                        out_file.write(f'            "{extension}"\n')
                    out_file.write('        ],\n')

                Package._write_string_entry_from_value(out_file, 'size_exact',
                                                       self._config.file_slot_required_size(slot_id))
                Package._write_string_entry_from_value(out_file, 'size_maximum',
                                                       self._config.file_slot_maximum_size(slot_id))
                Package._write_string_entry_from_value(out_file, 'address',
                                                       self._config.file_slot_address(slot_id))
                Package._write_string_entry_from_value(out_file, 'filename',
                                                       self._config.file_slot_filename(slot_id))

                out_file.write('      }')

                found_a_slot = True

            if found_a_slot:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generate_interact_file(self) -> None:
        with open(self._cores_folder / 'interact.json', 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "interact": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variables": [')

            found_a_variable = False
            for variable_id in self._config.variable_list():
                if found_a_variable:
                    out_file.write(',')

                out_file.write('\n      {\n')
                out_file.write(f'        "name": "{self._config.variable_name(variable_id)}",\n')
                out_file.write(f'        "id": {variable_id},\n')
                variable_type = self._config.variable_type(variable_id)
                out_file.write(f'        "type": "{variable_type}",\n')
                enabled_string = "true" if self._config.variable_is_enabled(variable_id) else "false"
                out_file.write(f'        "enabled": {enabled_string},\n')

                match variable_type:
                    case 'radio' | 'check':
                        Package._write_boolean_entry_from_value(out_file, 'persist',
                                                                self._config.variable_is_persistent(variable_id))
                        Package._write_boolean_entry_from_value(out_file, 'writeonly',
                                                                self._config.variable_is_write_only(variable_id))
                        Package._write_string_entry_from_value(out_file, 'group',
                                                               self._config.variable_group(variable_id))
                        out_file.write(f'        "defaultval": '
                                       f'{1 if self._config.variable_default_boolean_value(variable_id) else 0},\n')
                        Package._write_string_entry_from_value(out_file, 'value',
                                                               self._config.variable_value_on(variable_id))
                        Package._write_string_entry_from_value(out_file, 'value_off',
                                                               self._config.variable_value_off(variable_id))
                        Package._write_string_entry_from_value(out_file, 'mask',
                                                               self._config.variable_mask(variable_id))
                    case 'slider_u32' | 'list':
                        Package._write_boolean_entry_from_value(out_file, 'persist',
                                                                self._config.variable_is_persistent(variable_id))
                        Package._write_boolean_entry_from_value(out_file, 'writeonly',
                                                                self._config.variable_is_write_only(variable_id))
                        Package._write_string_entry_from_value(out_file, 'defaultval',
                                                               self._config.variable_default_int_or_hex_value(
                                                                   variable_id))
                        Package._write_string_entry_from_value(out_file, 'mask',
                                                               self._config.variable_mask(variable_id))

                        if variable_type == 'slider_u32':
                            out_file.write('          "graphical": {\n')
                            Package._write_boolean_entry_from_value(out_file, 'signed',
                                                                    self._config.variable_value_is_signed(variable_id),
                                                                    extra_spaces='  ')
                            Package._write_string_entry_from_value(out_file, 'min',
                                                                   self._config.variable_minimum_value(variable_id),
                                                                   extra_spaces='  ')
                            Package._write_string_entry_from_value(out_file, 'max',
                                                                   self._config.variable_maximum_value(variable_id),
                                                                   extra_spaces='  ')
                            Package._write_string_entry_from_value(out_file, 'adjust_small',
                                                                   self._config.variable_small_step(variable_id),
                                                                   extra_spaces='  ')
                            Package._write_string_entry_from_value(out_file, 'adjust_large',
                                                                   self._config.variable_large_step(variable_id),
                                                                   extra_spaces='  ')
                            out_file.write('          }\n')
                        else:
                            found_an_option: bool = False

                            out_file.write('        "options": [')
                            for option in self._config.variable_options(variable_id):
                                if found_an_option:
                                    out_file.write(',')

                                out_file.write('\n          {\n')
                                Package._write_string_entry_from_value(out_file, 'value', option[1],
                                                                       extra_spaces='    ')
                                out_file.write('            "name": "{option[0]}"\n')
                                out_file.write('          }')

                                found_an_option = True

                            out_file.write('\n        ]\n')
                    case 'action':
                        Package._write_string_entry_from_value(out_file, 'value',
                                                               self._config.variable_value(variable_id))
                        Package._write_string_entry_from_value(out_file, 'mask',
                                                               self._config.variable_mask(variable_id))

                address = self._config.variable_address(variable_id)
                address_string = f'"{address}"' if address.startswith('0x') else address
                out_file.write(f'        "address": {address_string}\n')
                out_file.write('      }')

                found_a_variable = True

            if found_a_variable:
                out_file.write('\n    ')

            out_file.write('],\n')
            out_file.write('    "messages": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generate_core_file(self) -> None:
        with open(self._cores_folder / 'core.json', 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "core": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "metadata": {\n')
            out_file.write('      "platform_ids": ["%s"],\n' % (self._config.platform_short_name()))
            out_file.write('      "shortname": "%s",\n' % (self._config.platform_short_name()))
            out_file.write('      "description": "%s",\n' % (self._config.platform_description()))
            out_file.write('      "author": "%s",\n' % (self._config.author_name()))
            out_file.write('      "url": "%s",\n' % (self._config.author_url()))
            out_file.write('      "version": "%s",\n' % (self._config.build_version()))
            out_file.write('      "date_release": "%s"\n' % self._today)
            out_file.write('    },\n')
            out_file.write('    "framework": {\n')
            out_file.write('      "target_product": "Analogue Pocket",\n')
            out_file.write('      "version_required": "1.1",\n')
            out_file.write('      "sleep_supported": false,\n')
            out_file.write('      "dock": {\n')
            out_file.write('        "supported": true,\n')
            out_file.write('        "analog_output": false\n')
            out_file.write('      },\n')
            out_file.write('      "hardware": {\n')
            out_file.write('        "link_port": %s,\n' % ('true' if self._config.link_port() else 'false'))
            out_file.write('        "cartridge_adapter": %d\n' % (0 if self._config.power_cartridge_port() else -1))
            out_file.write('      }\n')
            out_file.write('    },\n')

            found_a_core: bool = False
            out_file.write('    "cores": [')
            for core_id in self._config.cores_list():
                if found_a_core:
                    out_file.write(',')

                out_file.write('\n      {\n')

                core_name = self._config.core_name(core_id)
                if core_name is not None:
                    out_file.write(f'        "name": "{core_name}",\n')

                out_file.write(f'        "id": {core_id},\n')
                out_file.write(f'        "filename": "{self._config.core_filename(core_id)}"\n')
                out_file.write('      }')

                found_a_core = True

            if found_a_core:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generate_input_file(self) -> None:
        with open(self._cores_folder / 'input.json', 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "input": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "controllers": [')

            found_a_controller: bool = False
            for controller_id in self._config.controller_list():
                if found_a_controller:
                    out_file.write(',')

                out_file.write('\n      {\n')

                out_file.write('        "type": "default",\n')
                out_file.write('        "mappings": [')

                mapping_id: int = 0
                for mapping in self._config.controller_key_mapping(controller_id):
                    if mapping_id != 0:
                        out_file.write(',')

                    out_file.write('\n          {\n')
                    out_file.write(f'            "id": {mapping_id},\n')
                    out_file.write(f'            "name": "{mapping[0]}",\n')
                    out_file.write(f'            "key": "{mapping[1]}"\n')
                    out_file.write('          }')

                    mapping_id += 1

                out_file.write('\n        ]\n')
                out_file.write('      }')

                found_a_controller = True

            if found_a_controller:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generate_definition_files(self) -> None:
        output_filename = self._cores_folder / 'audio.json'
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "audio": {\n')
            out_file.write('    "magic": "APF_VER_1"\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generate_data_file()
        self._generate_input_file()

        output_filename = self._cores_folder / 'variants.json'
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "variants": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variant_list": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generate_interact_file()

        output_filename = self._cores_folder / 'video.json'
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "video": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "scaler_modes": [\n')
            out_file.write('      {\n')
            out_file.write('        "width": %d,\n' % (self._config.video_width()))
            out_file.write('        "height": %d,\n' % (self._config.video_height()))
            out_file.write('        "aspect_w": %d,\n' % (self._config.video_horizontal_aspect_ratio()))
            out_file.write('        "aspect_h": %d,\n' % (self._config.video_vertical_aspect_ratio()))
            out_file.write('        "rotation": %d,\n' % (self._config.video_rotation_angle()))

            flip_video: int = 0
            if self._config.video_flip_horizontal():
                flip_video |= 2
            if self._config.video_flip_vertical():
                flip_video |= 1

            out_file.write('        "mirror": %d\n' % flip_video)
            out_file.write('      }\n')

            display_modes: List[str] = self._config.display_modes()
            if len(display_modes):
                out_file.write('    ],\n')
                out_file.write('    "display_modes": [\n')

                for display_mode in display_modes:
                    out_file.write('      {\n')
                    out_file.write('        "id": "%s"\n' % display_mode)
                    out_file.write('      }')
                    if display_modes.index(display_mode) < len(display_modes):
                        out_file.write(',\n')
                    else:
                        out_file.write('\n')

                out_file.write('    ]\n')
            else:
                out_file.write('    ]\n')

            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = self._platforms_folder / f'{self._config.platform_short_name()}.json'
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "platform": {\n')
            out_file.write('    "category": "%s",\n' % (self._config.platform_category()))
            out_file.write('    "name": "%s",\n' % (self._config.platform_name()))
            out_file.write('    "year": %s,\n' % (self._today.split('-')[0]))
            out_file.write('    "manufacturer": "%s"\n' % (self._config.author_name()))
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generate_core_file()

    def _add_images(self) -> None:
        src_image = self._config.platform_image()
        dest_bin_file = self._platforms_images_folder / f'{self._config.platform_short_name()}.bin'

        if src_image.suffix == '.bin':
            shutil.copyfile(src_image, dest_bin_file)
        else:
            Convert([str(src_image), str(dest_bin_file)], debug_on=self._debug_on).run()

        src_image = self._config.author_icon()
        dest_bin_file = self._cores_folder / 'icon.bin'

        if src_image.suffix == '.bin':
            shutil.copyfile(src_image, dest_bin_file)
        else:
            Convert([str(src_image), str(dest_bin_file)], debug_on=self._debug_on).run()

    def _add_assets_if_needed(self) -> None:
        files_already_copied: List[str] = []

        found_assets_to_add: bool = False

        for file_slot_id in self._config.file_slot_list():
            files_to_include = self._config.file_slot_files_to_include(file_slot_id)

            file_path = self._config.file_slot_file_path(file_slot_id)
            if file_path is not None:
                files_to_include.append(file_path)

            for file_to_include in files_to_include:
                if not found_assets_to_add:
                    print('Adding core assets...')
                    os.makedirs(self._assets_folder, exist_ok=True)

                    found_assets_to_add = True

                filename = file_to_include.name
                if filename in files_already_copied:
                    raise ArgumentError(f'File {filename} is included twice in the core.')

                files_already_copied.append(filename)

                destination_path = self._assets_folder / filename
                shutil.copyfile(file_to_include, destination_path)

    def _package_core(self) -> None:
        packaged_filename = (self._destination_folder / self.packaged_filename()).absolute()
        if packaged_filename.exists():
            os.remove(packaged_filename)

        with zipfile.ZipFile(packaged_filename, 'w') as myzip:
            for p in Path(self._packaging_folder).rglob('*'):
                if p.is_dir():
                    continue

                relative_path = p.relative_to(self._packaging_folder)
                print(f'   adding "{relative_path}"')
                myzip.write(p, arcname=relative_path, compress_type=zipfile.ZIP_DEFLATED)

    def dependencies(self) -> List[Path]:
        deps: List[Path] = [self._config.config_file(),
                            self._config.platform_image(),
                            self._config.author_icon()]

        for file in self._bitstream_files:
            # -- First entry is the source bitstream file.
            deps.append(file[0])

        info_file = self._config.platform_info_file()
        if info_file is not None:
            deps.append(info_file)

        for file_slot_id in self._config.file_slot_list():
            files_to_include = self._config.file_slot_files_to_include(file_slot_id)

            file_path = self._config.file_slot_file_path(file_slot_id)
            if file_path is not None:
                files_to_include.append(file_path)

            for file_to_include in files_to_include:
                deps.append(file_to_include)

        return deps

    def packaged_filename(self) -> str:
        return '%s-%s-%s.zip' % (self._config.full_platform_name(), self._config.build_version(), self._today)

    def run(self) -> None:
        try:
            # -- We delete the core packaging folder in case stale files are in there (for example after
            # -- changing the core config file)
            if self._packaging_folder.exists():
                shutil.rmtree(self._packaging_folder)

            os.makedirs(self._packaging_folder)
            os.makedirs(self._cores_folder, exist_ok=True)
            os.makedirs(self._platforms_folder, exist_ok=True)
            os.makedirs(self._platforms_images_folder, exist_ok=True)

            print('Reversing bitstream files...')
            for file in self._bitstream_files:
                Reverse([str(file[0]), str(self._cores_folder / file[1])],
                        debug_on=self._debug_on).run()

            print('Generating definitions files...')
            self._generate_definition_files()

            print('Adding images...')
            self._add_images()

            self._add_assets_if_needed()

            info_file = self._config.platform_info_file()
            if info_file is not None:
                dest_info = self._cores_folder / 'info.txt'
                shutil.copyfile(info_file, dest_info)

            print('Packaging core...')
            self._package_core()
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while packaging core.')

            sys.exit(1)
