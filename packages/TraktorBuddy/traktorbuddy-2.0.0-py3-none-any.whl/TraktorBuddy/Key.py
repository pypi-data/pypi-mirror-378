#
# Copyright (c) 2022-present Didier Malenfant <didier@malenfant.net>
#
# This file is part of TraktorBuddy.
#
# TraktorBuddy is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TraktorBuddy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with TraktorBuddy. If not,
# see <https://www.gnu.org/licenses/>.
#

from enum import IntEnum, unique


@unique
class OpenNotation(IntEnum):
    Key_1d = 0    # -- C
    Key_8d = 1    # -- CsDb
    Key_3d = 2    # -- D
    Key_10d = 3   # -- DsEb
    Key_5d = 4    # -- E
    Key_12d = 5   # -- F
    Key_7d = 6    # -- FsGb
    Key_2d = 7    # -- G
    Key_9d = 8    # -- GsAb
    Key_4d = 9    # -- A
    Key_11d = 10  # -- AsBb
    Key_6d = 11   # -- B
    Key_10m = 12  # -- Cm
    Key_5m = 13   # -- CsmDbm
    Key_12m = 14  # -- Dm
    Key_7m = 15   # -- DsmEbm
    Key_2m = 16   # -- Em
    Key_9m = 17   # -- Fm
    Key_4m = 18   # -- FsmGbm
    Key_11m = 19  # -- Gm
    Key_6m = 20   # -- GsmAbm
    Key_1m = 21   # -- Am
    Key_8m = 22   # -- AsmBbm
    Key_3m = 23   # -- Bm
