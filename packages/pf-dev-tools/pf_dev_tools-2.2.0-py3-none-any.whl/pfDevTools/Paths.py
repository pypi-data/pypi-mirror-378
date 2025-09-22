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

import tempfile

from pathlib import Path


class Paths:
    """Various paths used by pfDevTools."""

    @classmethod
    def temp_folder(cls) -> Path:
        return Path(tempfile.gettempdir()) / 'io.project-freedom'

    @classmethod
    def app_update_check_file(cls) -> Path:
        return Paths.temp_folder() / 'app-update-check'
