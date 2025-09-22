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

import semver

from pfDevTools.PfCommand.Clean import Clean
from pfDevTools.PfCommand.Clone import Clone
from pfDevTools.PfCommand.Convert import Convert
from pfDevTools.PfCommand.Delete import Delete
from pfDevTools.PfCommand.DryRun import DryRun
from pfDevTools.PfCommand.Eject import Eject
from pfDevTools.PfCommand.Install import Install
from pfDevTools.PfCommand.Make import Make
from pfDevTools.PfCommand.Qfs import Qfs
from pfDevTools.PfCommand.Reverse import Reverse
from pfDevTools.Package import Package
from pfDevTools.CoreConfig import CoreConfig
from pfDevTools.Paths import Paths
from pfDevTools.SConsEnv import scons_environment

from .__about__ import __version__

__all__ = ['Clean', 'Clone', 'Convert', 'Delete', 'DryRun', 'Eject', 'Install', 'Make', 'Qfs', 'Reverse',
           'Package', 'CoreConfig', 'Paths', 'scons_environment']


# --- Makes sure current pfDevTools versions is supported
def requires(version: str) -> None:
    current = semver.Version.parse(__version__, optional_minor_and_patch=True)
    required = semver.Version.parse(version, optional_minor_and_patch=True)

    if (not (required.major == current.major) and
        ((current.minor > required.minor) or ((current.minor == required.minor) and
                                              (current.patch >= required.patch))) and
            (required.prerelease == current.prerelease)):
        raise RuntimeError(f'pfDevTools v{str(current)} is not compatible with the required version v{str(required)}.')
