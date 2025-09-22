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

from typing import List


# -- Classes
class Command:
    """A base command class."""

    @classmethod
    def name(cls) -> str:
        raise RuntimeError('Base class method call.')

    @classmethod
    def usage(cls) -> None:
        raise RuntimeError('Base class method call.')

    def __init__(self, arguments: List[str], debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._arguments = arguments
        self._debug_on = debug_on

        raise RuntimeError('Base class method call.')

    def run(self) -> None:
        raise RuntimeError('Base class method call.')
