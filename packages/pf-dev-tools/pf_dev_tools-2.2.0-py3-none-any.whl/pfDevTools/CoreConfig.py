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
import sys
import getpass

from typing import List, Dict, Optional, Any
from sys import platform
from enum import IntFlag
from pathlib import Path

from PyUtilities.Exceptions import ArgumentError

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        # -- This is just to quiet a warning about tomllib not defined in this case
        import enum as tomllib  # type: ignore[no-redef]
        sys.exit('Error: This program requires either tomllib or tomli but neither is available')


# -- Constants
class FileParameter(IntFlag):
    USER_RELOADABLE = 0x0001
    CORE_SPECIFIC = 0x0002
    NON_VOLATILE_FILENAME = 0x0004
    READ_ONLY = 0x0008
    INSTANCE_JSON = 0x0010
    INIT_NON_VOLATILE_DATA_ON_LOAD = 0x0020
    RESET_CORE_WHILE_LOADING = 0x0040
    RESTART_CORE_AFTER_LOADING = 0x0080
    FULL_RELOAD_CORE = 0x0100
    PERSIST_BROWSED_FILENAME = 0x0200


# -- Classes
class CoreConfig:
    """A class for openFPGA core configurations"""

    @classmethod
    def _greatest_common_factor(cls, a: int, b: int) -> int:
        return abs(a) if b == 0 else CoreConfig._greatest_common_factor(b, a % b)

    @classmethod
    def core_install_volume_path(cls) -> Path:
        volume_path = os.environ.get('PF_CORE_INSTALL_PATH')
        if volume_path is None:
            if platform == 'darwin':
                return Path('/Volumes/POCKET')
            elif platform == 'linux':
                return Path('/media') / getpass.getuser() / 'POCKET'
            elif platform == 'win32':
                return Path('P:')
            else:
                raise ArgumentError(f'Unsupported platform "{platform}".')
        else:
            raise RuntimeError('PF_CORE_INSTALL_PATH is not defined in the environment.')

    @classmethod
    def _numeric_value_to_string(cls, value: Optional[Any],
                                 signed_allowed: bool = False,
                                 default: Optional[str] = None) -> Optional[str]:
        if value is None:
            return default

        if isinstance(value, str):
            if not value.startswith('0x') or len(value) > 10:
                return None

            try:
                int(value[2:], 16)
            except ValueError:
                return None

            return value
        elif isinstance(value, int):
            if signed_allowed:
                if value > 2147483647 or value < -2147483648:
                    return None
            elif value < 0:
                return None

            if value > 0xFFFFFFFF:
                return None

            return f"{value}"
        else:
            return None

    @classmethod
    def core_section_name(cls, core_id: str) -> str:
        return f'Cores.{core_id}'

    @classmethod
    def file_slot_section_name(cls, slot_id: str) -> str:
        return f'Files.{slot_id}'

    @classmethod
    def variable_section_name(cls, variable_id: str) -> str:
        return f'Variables.{variable_id}'

    @classmethod
    def controller_section_name(cls, controller_id: str) -> str:
        return f'Controllers.{controller_id}'

    def __init__(self, config_file: Path):
        """Constructor based on config file path."""

        self._config_file = config_file
        self._platform_short_name: Optional[str] = None
        self._video_width: Optional[int] = None
        self._video_height: Optional[int] = None
        self._video_ratio_gcf: Optional[int] = None

        if self._config_file.suffix != '.toml':
            raise ArgumentError('Config file needs to be a toml file.')

        if not self._config_file.exists():
            raise ArgumentError(f'Config file "{str(self._config_file)}" does not exist.')

        self.config_file_folder = self._config_file.parent

        with open(self._config_file, mode="rb") as fp:
            self._config = tomllib.load(fp)

        # -- If no cores are specified, we default to this single one.
        if self._config.get('Cores', None) is None:
            self._config['Cores'] = {'0': {'name': 'default',
                                           'source_file': 'pf_core.rbf',
                                           'filename': 'bitstream.rbf_r'}}

    def _get_config_category(self, category_name: str) -> Dict[str, Any]:
        content = self._config.get(category_name, {})
        if type(content) is not Dict:
            raise ArgumentError(f'Category "{category_name}" in config file contains invalid data.')

        return content

    def _get_config_param(self, section_name: str, param_name: str) -> Optional[Any]:
        section: Dict[str, Any] = {}

        section_name_parts = section_name.split('.')
        number_of_parts = len(section_name_parts)
        if number_of_parts > 1:
            if number_of_parts > 2:
                raise ArgumentError(f'Invalid section named {section_name} is being searched config file.')

            from_config = self._get_config_category(section_name_parts[0])
            if from_config is not None:
                content = from_config.get(section_name_parts[1])
                if type(content) is not Dict:
                    raise ArgumentError(f'Parameter "{section_name}" in config file contains invalid data.')
        else:
            section = self._get_config_category(section_name)

        return section.get(param_name)

    def _read_value_from_config_param(self, section_name: str, param_name: str,
                                      value_type: type, default: Optional[Any] = None) -> Any:
        value = self._get_config_param(section_name, param_name)
        if value is not None:
            if not isinstance(value, value_type):
                raise ArgumentError(f'Found invalid value "{value}" for "{param_name}" in "{section_name}". '
                                    f'Should be a {str(value_type)}.')

            return value

        if default is not None:
            if not isinstance(default, value_type):
                raise RuntimeError(f'Invalid default value "{default}" for "{param_name}" in "{section_name}". '
                                   f'Should be a {str(value_type)}.')

            return default

        raise ArgumentError(f'Found no value for "{param_name}" in "{section_name}". ')

    def _read_boolean_from_config_param(self, section_name: str, param_name: str,
                                        default: Optional[bool] = None) -> bool:
        return bool(self._read_value_from_config_param(section_name, param_name, value_type=bool, default=default))

    def _read_boolean_from_file_param(self, slot_id: str, param_name: str, default: Optional[bool] = None) -> bool:
        return bool(self._read_value_from_config_param(CoreConfig.file_slot_section_name(slot_id), param_name,
                                                       value_type=bool, default=default))

    def _read_boolean_from_variable_param(self, variable_id: str, param_name: str,
                                          default: Optional[bool] = None) -> bool:
        return bool(self._read_value_from_config_param(CoreConfig.variable_section_name(variable_id), param_name,
                                                       value_type=bool, default=default))

    def _read_string_from_config_param(self, section_name: str, param_name: str,
                                       default: Optional[str] = None) -> str:
        return str(self._read_value_from_config_param(section_name, param_name, value_type=str, default=default))

    def _read_int_from_config_param(self, section_name: str, param_name: str,
                                    default: Optional[int] = None) -> int:
        return int(self._read_value_from_config_param(section_name, param_name, value_type=int, default=default))

    def _read_list_from_config_param(self, section_name: str, param_name: str,
                                     default: Optional[List[Any]] = None) -> List[Any]:
        return List(self._read_value_from_config_param(section_name, param_name, value_type=List, default=default))

    def _read_numeric_value_from_config_param(self, section_name: str, param_name: str, signed_allowed: bool = False,
                                              default: Optional[str] = None) -> Optional[str]:
        return CoreConfig._numeric_value_to_string(self._get_config_param(section_name, param_name),
                                                   signed_allowed=signed_allowed, default=default)

    def _get_video_ratio_gcf(self) -> int:
        if self._video_ratio_gcf is None:
            self._video_ratio_gcf = CoreConfig._greatest_common_factor(int(self.video_width()),
                                                                       int(self.video_height()))

        return self._video_ratio_gcf

    def config_file(self) -> Path:
        return self._config_file

    def platform_name(self) -> str:
        platform_name = self._read_string_from_config_param('Platform', 'name')
        if len(platform_name) > 31:
            raise ArgumentError(f'Invalid platform name "{platform_name}". Maximum length is 31 characters.')

        return platform_name

    def platform_image(self) -> Path:
        platform_image = self._read_string_from_config_param('Platform', 'image')
        return self.config_file_folder / platform_image

    def platform_short_name(self) -> str:
        if self._platform_short_name is None:
            self._platform_short_name = self._read_string_from_config_param('Platform',
                                                                            'short_name')

            if len(self._platform_short_name) > 31:
                raise ArgumentError(f'Invalid platform short name "{self._platform_short_name}". '
                                    f'Maximum length is 31 characters.')

            for c in self._platform_short_name:
                if (c.isalnum() is False) or c.isupper():
                    raise ArgumentError(f'Invalid platform short name "{self._platform_short_name}". '
                                        f'Should be lower-case and can only contain a-z, 0-9 or _.')

        return self._platform_short_name

    def platform_category(self) -> str:
        category = self._read_string_from_config_param('Platform', 'category')
        if len(category) > 31:
            raise ArgumentError(f'Invalid platform category "{category}". Maximum length is 31 characters.')

        return category

    def platform_description(self) -> str:
        value = self._read_string_from_config_param('Platform', 'description')
        if len(value) > 63:
            raise ArgumentError(f'Invalid platform description "{value}". Maximum length is 63 characters.')

        return value

    def platform_info_file(self) -> Optional[Path]:
        info_file = self._read_string_from_config_param('Platform', 'info', default='')
        if len(info_file) == 0:
            return None

        return Path(os.path.expandvars(self.config_file_folder / info_file))

    def cores_list(self) -> List[str]:
        cores = list(self._get_config_category('Cores').keys())
        if len(cores) == 0:
            raise ArgumentError('Did not find any cores to build in the config file.')
        if len(cores) > 8:
            raise ArgumentError('Found more than 8 cores in the config file.')

        for core_id in cores:
            if int(core_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid core id "{CoreConfig.core_section_name(core_id)}". '
                                    f'ID should fit in a 16-bit unsigned.')

        return cores

    def core_name(self, core_id: str) -> Optional[str]:
        core_section_name = CoreConfig.core_section_name(core_id)
        core_name = self._read_string_from_config_param(core_section_name, 'name', default='')
        if len(core_name) == 0:
            return None
        if len(core_name) > 15:
            raise ArgumentError(f'Found invalid core name for "{core_section_name}". '
                                f'Maximum length is 15 characters.')

        return core_name

    def core_filename(self, core_id: str) -> str:
        core_section_name = CoreConfig.core_section_name(core_id)
        filename = self._read_string_from_config_param(core_section_name, 'filename')
        if len(filename) > 15:
            raise ArgumentError(f'Found invalid core filename for "{core_section_name}". '
                                f'Maximum length is 15 characters.')

        return filename

    def core_source_file(self, core_id: str) -> str:
        return self._read_string_from_config_param(CoreConfig.core_section_name(core_id), 'source_file')

    def build_version(self) -> str:
        value = self._read_string_from_config_param('Build', 'version')
        if len(value) > 31:
            raise ArgumentError(f'Invalid platform version "{value}". Maximum length is 31 characters.')

        return value

    def author_name(self) -> str:
        value = self._read_string_from_config_param('Author', 'name')
        if len(value) > 31:
            raise ArgumentError(f'Invalid platform author "{value}". Maximum length is 31 characters.')

        return value

    def author_icon(self) -> Path:
        return self.config_file_folder / self._read_string_from_config_param('Author', 'icon')

    def author_url(self) -> str:
        value = self._read_string_from_config_param('Author', 'url')
        if len(value) > 63:
            raise ArgumentError(f'Invalid platform URL "{value}". Maximum length is 63 characters.')

        return value

    def video_width(self) -> int:
        if self._video_width is None:
            self._video_width = self._read_int_from_config_param('Hardware', 'video_width')

        return self._video_width

    def video_height(self) -> int:
        if self._video_height is None:
            self._video_height = self._read_int_from_config_param('Hardware', 'video_height')

        return self._video_height

    def video_horizontal_aspect_ratio(self) -> int:
        common_factor = self._get_video_ratio_gcf()
        if common_factor == 1:
            raise ArgumentError(f'Could not find a valid common factor for aspect ratio given a resolution of '
                                f'{self.video_width()}x{self.video_height()}.')

        return int(self.video_width() / common_factor)

    def video_vertical_aspect_ratio(self) -> int:
        common_factor = self._get_video_ratio_gcf()
        if common_factor == 1:
            raise ArgumentError(f'Could not find a valid common factor for aspect ratio given a resolution of '
                                f'{self.video_width()}x{self.video_height()}.')

        return int(self.video_height() / common_factor)

    def video_rotation_angle(self) -> int:
        value = self._read_int_from_config_param('Hardware', 'video_rotation_angle', default=0)
        if value != 0 and value != 90 and value != 180 and value != 270:
            raise ArgumentError(f'Invalid platform video_rotation_angle "{value}". Should be 0, 90, 180 or 270.')

        return value

    def video_flip_horizontal(self) -> bool:
        return self._read_boolean_from_config_param('Hardware', 'video_flip_horizontal',
                                                    default=False)

    def video_flip_vertical(self) -> bool:
        return self._read_boolean_from_config_param('Hardware', 'video_flip_vertical',
                                                    default=False)

    def link_port(self) -> bool:
        return self._read_boolean_from_config_param('Hardware',
                                                    'link_port',
                                                    default=False)

    def power_cartridge_port(self) -> bool:
        return self._read_boolean_from_config_param('Hardware',
                                                    'power_cartridge_port',
                                                    default=False)

    def display_modes(self) -> List[str]:
        values: Dict[str, str] = {
            'crt_trinitron': '0x10',
            'grayscale_lcd': '0x20',
            'original_gb_dmg': '0x21',
            'original_gbp': '0x22',
            'original_gbp_light': '0x23',
            'reflective_color': '0x30',
            'original_gbc': '0x31',
            'original_gbc+': '0x32',
            'backlit_color': '0x40',
            'original_gba': '0x41',
            'original_gba_sp101': '0x42',
            'original_gg': '0x51',
            'original_gg+': '0x52',
            'pinball_neon_matrix': '0xE0'
        }
        selected_display_modes = self._read_list_from_config_param('Hardware', 'display_modes',
                                                                   default=[])
        output_list: List[str] = []

        for display_mode in selected_display_modes:
            display_code = values[display_mode]
            if display_code is None or not isinstance(display_code, str):
                raise ArgumentError(f'Found invalid display mode "{display_mode}".')
            output_list.append(display_code)

        return output_list

    def full_platform_name(self) -> str:
        return f'{self.author_name()}.{self.platform_short_name()}'

    def file_slot_list(self) -> List[str]:
        file_slots = list(self._get_config_category('Files').keys())
        if len(file_slots) > 32:
            raise ArgumentError('Found more than 32 file slots in the config file.')

        for slot_id in file_slots:
            if int(slot_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid file slot id "{CoreConfig.file_slot_section_name(slot_id)}". '
                                    f'Must be a 16-bit unsigned integer.')

        return file_slots

    def file_slot_name(self, slot_id: str) -> str:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        slot_name = self._read_string_from_config_param(file_section_name, 'name')
        if len(slot_name) > 15:
            raise ArgumentError(f'Found invalid slot name for "{file_section_name}". '
                                f'Maximum length is 15 characters.')

        return slot_name

    def file_slot_required(self, slot_id: str) -> bool:
        return self._read_boolean_from_file_param(slot_id, 'required', default=True)

    def file_slot_defer_loading(self, slot_id: str) -> bool:
        return self._read_boolean_from_file_param(slot_id, 'defer_loading', default=False)

    def file_slot_secondary(self, slot_id: str) -> bool:
        return self._read_boolean_from_file_param(slot_id, 'secondary', default=False)

    def file_slot_non_volatile(self, slot_id: str) -> bool:
        return self._read_boolean_from_file_param(slot_id, 'non_volatile', default=False)

    def file_slot_parameters(self, slot_id: str) -> int:
        values: Dict[str, int] = {
            'user-reloadable': FileParameter.USER_RELOADABLE,
            'core-specific': FileParameter.CORE_SPECIFIC,
            'non-volatile-filename': FileParameter.NON_VOLATILE_FILENAME,
            'read-only': FileParameter.READ_ONLY,
            'instance-json': FileParameter.INSTANCE_JSON,
            'init-non-volatile-data-on-load': FileParameter.INIT_NON_VOLATILE_DATA_ON_LOAD,
            'reset-core-while-loading': FileParameter.RESET_CORE_WHILE_LOADING,
            'restart-core-after-loading': FileParameter.RESTART_CORE_AFTER_LOADING,
            'full-reload-core': FileParameter.FULL_RELOAD_CORE,
            'persist-browsed-filename': FileParameter.PERSIST_BROWSED_FILENAME
        }

        parameters = 0

        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        params = self._read_list_from_config_param(file_section_name, 'parameters', default=[])
        for param in params:
            bit_value = values.get(param, None)
            if bit_value is None:
                raise ArgumentError(f'Unknown data slot parameter "{param}" for file slot "{file_section_name}".')

            parameters |= bit_value

        if parameters & FileParameter.INSTANCE_JSON and not parameters & FileParameter.CORE_SPECIFIC:
            raise ArgumentError(f'"core-specific" parameter is required if "instance-json" is used '
                                f'for file slot "{file_section_name}".')

        return parameters

    def file_slot_extensions(self, slot_id: str) -> List[str]:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        extensions = self._read_list_from_config_param(file_section_name, 'extensions', default=[])
        if len(extensions) > 4:
            raise ArgumentError(f'Too many extensions for file slot "{file_section_name}". Limit is 4.')

        for extension in extensions:
            if not isinstance(extension, str) or len(extension) > 7:
                raise ArgumentError(f'Invalid extension "{extension}" file slot "{file_section_name}". '
                                    f'Should be a string of 7 characters maximum.')

        return extensions

    def file_slot_required_size(self, slot_id: str) -> Optional[str]:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        size = self._read_numeric_value_from_config_param(file_section_name, 'required_size',
                                                          default='')
        if size:
            raise ArgumentError(f'Invalid required size for "{file_section_name}". '
                                f'Should be a 32-bit unsigned integer or hex string with 0x prefix.')

        return size

    def file_slot_maximum_size(self, slot_id: str) -> Optional[str]:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        size = self._read_numeric_value_from_config_param(file_section_name, 'maximum_size')
        if size is None:
            raise ArgumentError(f'Invalid maximum size for "{file_section_name}". '
                                f'Should be a 32-bit unsigned integer or hex string with 0x prefix.')

        return size

    def file_slot_address(self, slot_id: str) -> str:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        address = self._read_numeric_value_from_config_param(file_section_name, 'address')
        if address is None:
            raise ArgumentError(f'Invalid address for "{file_section_name}". '
                                f'Should be a 32-bit unsigned integer or hex string with 0x prefix.')

        return address

    def file_slot_file_path(self, slot_id: str) -> Optional[Path]:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        file_path_as_string = self._read_string_from_config_param(file_section_name, 'filename', default='')
        if file_path_as_string == '':
            return None

        file_path = Path(os.path.expandvars(self.config_file_folder / file_path_as_string))
        if not file_path.exists():
            raise ArgumentError(f'Cannot find file "{file_path}" needed to include with the core.')

        return file_path

    def file_slot_filename(self, slot_id: str) -> Optional[str]:
        file_path = self.file_slot_file_path(slot_id)
        if file_path is None:
            return None

        base_filename = file_path.name
        if len(base_filename) > 31:
            file_section_name = CoreConfig.file_slot_section_name(slot_id)
            raise ArgumentError(f'Found invalid filename for "{file_section_name}". '
                                f'Maximum length is 31 characters.')

        return base_filename

    def file_slot_files_to_include(self, slot_id: str) -> List[Path]:
        file_section_name = CoreConfig.file_slot_section_name(slot_id)
        file_paths = self._read_list_from_config_param(file_section_name, 'include_files', default=[])

        files: List[Path] = []
        for file_path in file_paths:
            if not isinstance(file_paths, List):
                raise ArgumentError(f'Found invalid filename for "{file_section_name}". Should be a string.')

            filename = Path(file_path).name
            if len(filename) > 31:
                raise ArgumentError(f'Found invalid filename for "{file_section_name}". '
                                    f'Maximum length is 31 characters.')

            file_path = Path(os.path.expandvars(self.config_file_folder / file_path))
            if not file_path.exists():
                raise ArgumentError(f'Cannot find file "{file_path}" needed to include with the core.')

            files.append(file_path)

        return files

    def variable_list(self) -> List[str]:
        variables = list(self._get_config_category('Variables').keys())
        if len(variables) > 16:
            raise ArgumentError('Found more than 16 variables in the config file.')

        for variable_id in variables:
            if int(variable_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid variable id "{CoreConfig.variable_section_name(variable_id)}". '
                                    f'Must be a 16-bit unsigned integer.')

        return variables

    def variable_name(self, variable_id: str) -> str:
        variable_section_name = CoreConfig.variable_section_name(variable_id)
        variable_name = self._read_string_from_config_param(variable_section_name, 'name')
        if len(variable_name) > 23:
            raise ArgumentError(f'Found invalid variable name for "{variable_section_name}". '
                                f'Maximum length is 23 characters.')

        return variable_name

    def variable_type(self, variable_id: str) -> str:
        values: Dict[str, str] = {
            'radio_button': 'radio',
            'checkbox': 'check',
            'slider': 'slider_u32',
            'list': 'list',
            'number': 'number_u32',
            'action': 'action'
        }

        variable_section_name = CoreConfig.variable_section_name(variable_id)
        variable_type = self._read_string_from_config_param(variable_section_name, 'type')
        json_variable_type = values.get(variable_type, None)
        if json_variable_type is None:
            raise ArgumentError(f'Found invalid variable type "{variable_type}" for "{variable_section_name}".')

        return json_variable_type

    def variable_is_enabled(self, variable_id: str) -> bool:
        return self._read_boolean_from_variable_param(variable_id, 'enabled', default=True)

    def variable_address(self, variable_id: str) -> str:
        variable_section_name = CoreConfig.variable_section_name(variable_id)
        address = self._read_numeric_value_from_config_param(variable_section_name, 'address')
        if address is None:
            raise ArgumentError(f'Invalid "address" for "{variable_section_name}". '
                                f'Must be a 32-bit unsigned integer or hex string.')

        return address

    def variable_is_persistent(self, variable_id: str) -> bool:
        return self._read_boolean_from_variable_param(variable_id, 'persistent', default=False)

    def variable_is_write_only(self, variable_id: str) -> bool:
        return self._read_boolean_from_variable_param(variable_id, 'write-only', default=False)

    def variable_default_boolean_value(self, variable_id: str) -> bool:
        value = self._read_boolean_from_variable_param(variable_id, 'default')
        if value is None:
            raise ArgumentError(f'Invalid or missing "default" for '
                                f'"{CoreConfig.variable_section_name(variable_id)}".')

        return value

    def variable_int_or_hex_string_value(self, variable_id: str, value_name: str,
                                         signed_allowed: bool = False, default: Optional[str] = None) -> str:
        variable_section_name = CoreConfig.variable_section_name(variable_id)
        value_as_string = self._read_numeric_value_from_config_param(variable_section_name, value_name,
                                                                     signed_allowed=signed_allowed, default=default)
        if value_as_string is None:
            sign_string = 'signed' if signed_allowed else 'unsigned'
            raise ArgumentError(f'Invalid "{value_name}" for "{variable_section_name}". '
                                f'Must be a 32-bit {sign_string} integer or hex string.')

        return value_as_string

    def variable_group(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'group')

    def variable_value_on(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'value_on')

    def variable_value_off(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'value_off', default='0')

    def variable_mask(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'mask', default='0')

    def variable_default_int_or_hex_value(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'default')

    def variable_value(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'value', signed_allowed=True)

    def variable_value_is_signed(self, variable_id: str) -> bool:
        return self._read_boolean_from_variable_param(variable_id, 'signed_value', default=False)

    def variable_minimum_value(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'minimum_value',
                                                     signed_allowed=self.variable_value_is_signed(variable_id))

    def variable_maximum_value(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'maximum_value',
                                                     signed_allowed=self.variable_value_is_signed(variable_id))

    def variable_small_step(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'small_step',
                                                     signed_allowed=self.variable_value_is_signed(variable_id))

    def variable_large_step(self, variable_id: str) -> str:
        return self.variable_int_or_hex_string_value(variable_id, 'large_step',
                                                     signed_allowed=self.variable_value_is_signed(variable_id))

    def variable_options(self, variable_id: str) -> List[List[str]]:
        variable_section_name = CoreConfig.variable_section_name(variable_id)
        options = self._read_list_from_config_param(variable_section_name, 'choices', default=[])
        if len(options) > 16:
            raise ArgumentError(f'Too many options for variable "{variable_section_name}". Maximum supported is 16.')

        results: List[List[str]] = []
        for option in options:
            if not isinstance(option, List) or len(option) != 2:
                raise ArgumentError(f'Invalid option for variable "{variable_section_name}". '
                                    f'Format is [ <name>, <value> ].')

            name = option[0]
            if not isinstance(name, str) or len(name) > 23:
                raise ArgumentError(f'Invalid option name "{name}" for variable "{variable_section_name}". '
                                    f'Maximum length is 23 characters.')

            value_as_string = CoreConfig._numeric_value_to_string(option[1], signed_allowed=True)
            if value_as_string is None:
                raise ArgumentError(f'Invalid option value "{option[1]}" for variable "{variable_section_name}". '
                                    f'Must be a 32-bit integer or hex string.')

            results.append([name, value_as_string])

        return results

    def controller_list(self) -> List[str]:
        controllers = list(self._get_config_category('Controllers').keys())
        if len(controllers) > 4:
            raise ArgumentError('Found more than 4 controllers in the config file.')

        for controller_id in controllers:
            id_as_int = int(controller_id)
            if id_as_int < 1 or id_as_int > 4:
                raise ArgumentError(f'Found invalid controller id '
                                    f'"{CoreConfig.controller_section_name(controller_id)}". '
                                    f'ID should be between 1 and 4.')

        return controllers

    def controller_key_mapping(self, controller_id: str) -> List[List[str]]:
        values: Dict[str, str] = {
            'A': 'pad_btn_a',
            'B': 'pad_btn_b',
            'X': 'pad_btn_x',
            'Y': 'pad_btn_y',
            'L': 'pad_trig_l',
            'R': 'pad_trig_r',
            'Start': 'pad_btn_start',
            'Select': 'pad_btn_select',
        }

        controller_section_name = CoreConfig.controller_section_name(controller_id)
        mappings = self._read_list_from_config_param(controller_section_name, 'key_mapping', default=[])
        if len(mappings) > 8:
            raise ArgumentError(f'Found invalid mappings for controller id "{controller_section_name}". '
                                f'Should be a list of 8 mapping max.')

        results = []
        for mapping in mappings:
            if not isinstance(mapping, List) or len(mapping) != 2:
                raise ArgumentError(f'Invalid mapping for controller "{controller_section_name}". '
                                    f'Format is [ <name>, <button> ].')

            name = mapping[0]
            if not isinstance(name, str) or len(name) > 19:
                raise ArgumentError(f'Invalid mapping name "{name}" for controller "{controller_section_name}". '
                                    f'Should be string o 20 characters max.')

            button = values.get(mapping[1], None)
            if button is None:
                raise ArgumentError(f'Invalid button name "{mapping[1]}" for controller '
                                    f'"{controller_section_name}".')

            results.append([name, button])

        return results
