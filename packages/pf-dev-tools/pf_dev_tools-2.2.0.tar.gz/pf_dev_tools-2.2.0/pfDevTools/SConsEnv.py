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

import pfDevTools.OpenFPGACore

from SCons import Script as SConsScript
from SCons.Environment import Environment as SConsEnvironment
from typing import TypedDict
from pathlib import Path

from PyUtilities.Exceptions import DependencyError

try:
    from typing_extensions import Unpack
except ModuleNotFoundError:
    raise DependencyError('Cannot find Python type extensions. Maybe try "pip install typing_extensions".')


class SConsEnvironmentParams(TypedDict):
    PF_SRC_FOLDER: Path
    PF_CORE_FPGA_FOLDER: Path
    PF_CORE_TEMPLATE_REPO_FOLDER: Path
    PF_CORE_TEMPLATE_REPO_TAG: str
    PF_SKIP_BUILD: bool
    PF_DEBUG_ON: bool
    PF_EJECT_VOLUME: bool
    PF_ENABLE_OPTIMIZATION: bool
    PF_NB_OF_CPUS_TO_USE: int


def scons_environment(**kwargs: Unpack[SConsEnvironmentParams]) -> SConsEnvironment:
    SConsScript.AddOption(
        '--skip_build',
        action='store_true',
        help='Skip building the core',
        default=False
    )
    SConsScript.AddOption(
        '--debug_on',
        action='store_true',
        help='Enable debugging information',
        default=False
    )
    SConsScript.AddOption(
        '--eject',
        action='store_true',
        help='Eject volume after install',
        default=False
    )

    env = SConsEnvironment(**kwargs)

    env.AddMethod(pfDevTools.OpenFPGACore.build, 'OpenFPGACore')

    if SConsScript.GetOption('skip_build'):
        env['PF_SKIP_BUILD'] = True

    if SConsScript.GetOption('debug_on'):
        env['PF_DEBUG_ON'] = True

    if SConsScript.GetOption('eject'):
        env['PF_EJECT_VOLUME'] = True

    return env
