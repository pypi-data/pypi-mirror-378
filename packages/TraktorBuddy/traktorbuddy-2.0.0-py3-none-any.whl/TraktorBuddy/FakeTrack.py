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

import xml.etree.ElementTree as ElementTree
import PIL.Image

from datetime import datetime
from typing import Optional
from pathlib import Path

from TraktorBuddy.Key import OpenNotation
from TraktorBuddy.Rating import Rating
from TraktorBuddy.Color import Color
from TraktorBuddy.Track import Track


# -- Class
class FakeTrack(Track):
    """Interface for a Fake Traktor track used by the Listener."""

    def __init__(self, title: str, artist: str):
        """Constructor from a title and an artist."""

        super().__init__(entry_element=ElementTree.Element(''))

        self._title = title
        self._artist = artist

    def _mark_as_modified_now(self) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def has_stems_version_generated(self) -> bool:
        return False

    def is_a_sample(self) -> bool:
        return False

    def is_a_stem(self) -> bool:
        return False

    def is_a_cloud_file(self) -> bool:
        return False

    def matches_filter(self, filtered_by: int) -> bool:
        return False

    def file(self) -> Optional[Path]:
        return None

    def modification_date(self) -> Optional[datetime]:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def title(self) -> Optional[str]:
        return self._title

    def set_title(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def artist(self) -> Optional[str]:
        return self._artist

    def set_artist(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def beatgrid_locked(self) -> bool:
        return False

    def set_beat_grid_locked(self, value: bool, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def beatgrid_lock_modified_date(self) -> Optional[datetime]:
        return None

    def bitrate(self) -> Optional[int]:
        return None

    def set_bitrate(self, value: int, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def genre(self) -> Optional[str]:
        return None

    def set_genre(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def label(self) -> Optional[str]:
        return None

    def set_label(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def producer(self) -> Optional[str]:
        return None

    def set_producer(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def mix(self) -> Optional[str]:
        return None

    def set_mix(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def release(self) -> Optional[str]:
        return None

    def set_release(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def track_number(self) -> Optional[int]:
        return None

    def set_track_number(self, value: int, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def comments(self) -> Optional[str]:
        return None

    def set_comments(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def comments2(self) -> Optional[str]:
        return ''

    def set_comments2(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def remixer(self) -> Optional[str]:
        return None

    def set_remixer(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def key(self) -> Optional[str]:
        return None

    def set_key(self, value: str, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def play_count(self) -> Optional[int]:
        return None

    def set_play_count(self, value: int, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def length(self) -> Optional[float]:
        return None

    def set_length(self, value: float, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def rating(self) -> Optional[Rating]:
        return None

    def set_rating(self, value: Rating, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def import_date(self) -> Optional[datetime]:
        return None

    def set_import_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def last_played_date(self) -> Optional[datetime]:
        return None

    def set_last_played_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def release_date(self) -> Optional[datetime]:
        return None

    def set_release_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def file_size(self) -> Optional[int]:
        return None

    def set_file_size(self, value: int, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def bpm(self) -> Optional[float]:
        return None

    def set_bpm(self, value: float, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def traktor_key(self) -> Optional[OpenNotation]:
        return None

    def set_traktor_key(self, value: OpenNotation, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def color(self) -> Optional[Color]:
        return None

    def set_color(self, value: Color, mark_as_modified: bool = True) -> None:
        raise RuntimeError('Illegal call on a FakeTrack.')

    def cover_art_image_from_file(self) -> Optional[PIL.Image.Image]:
        return None

    def cover_art_cache_file(self) -> Optional[Path]:
        return None

    def cover_art_image_from_cache(self) -> Optional[PIL.Image.Image]:
        return None

    def stripe_file(self) -> Optional[Path]:
        return None

    def transients_file(self) -> Optional[Path]:
        return None

    def generated_stems_file(self) -> Optional[Path]:
        return None
