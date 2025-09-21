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
import mutagen

from datetime import datetime
from pathlib import Path
from io import BytesIO
from typing import Optional
from enum import IntEnum, unique

from PyUtilities import Utility
from TraktorBuddy.Key import OpenNotation
from TraktorBuddy.Rating import Rating
from TraktorBuddy.Color import Color
from TraktorBuddy.TraktorHash import TraktorHash


# -- Class
class Track:
    """Interface for Traktor tracks."""

    @unique
    class Filter(IntEnum):
        ONLY_TRACKS = 1
        ONLY_STEMS = 2
        ONLY_CLOUD_FILES = 3

    @classmethod
    def _get_from_element(cls, element: Optional[ElementTree.Element], name: str) -> Optional[str]:
        if element is None:
            return None

        return element.get(name)

    def __init__(self, entry_element: ElementTree.Element, collection_folder: Optional[Path] = None):
        """Constructor from an XML entry element."""

        self._entry_element = entry_element
        self._info_element = self._entry_element.find('INFO')
        self._album_element = self._entry_element.find('ALBUM')
        self._collection_folder = collection_folder

    def _get_entry_element(self) -> ElementTree.Element:
        return self._entry_element

    def _get_info_element(self, create_if_absent: bool = True) -> Optional[ElementTree.Element]:
        if self._info_element is None:
            if not create_if_absent:
                return None

            self._info_element = ElementTree.SubElement(self._entry_element, 'INFO')

            if self._info_element is None:
                raise RuntimeError('Error creating track INFO element.')

        return self._info_element

    def _get_album_element(self, create_if_absent: bool = True) -> Optional[ElementTree.Element]:
        if self._album_element is None:
            if not create_if_absent:
                return None

            self._album_element = ElementTree.SubElement(self._entry_element, 'ALBUM')

            if self._album_element is None:
                raise RuntimeError('Error creating track ALBUM element.')

        return self._album_element

    def _mark_as_modified_now(self) -> None:
        date = Utility.utc_time_now()

        self._entry_element.set('MODIFIED_DATE', date.strftime('%Y/%m/%d'))
        self._entry_element.set('MODIFIED_TIME', str(date.second + (date.minute * 60) + (date.hour * 3600)))

    def playlist_key(self) -> Optional[str]:
        location = self._entry_element.find('LOCATION')
        if location is None:
            return None

        webaddress = location.get('WEBADDRESS')
        if webaddress is not None:
            return webaddress

        volume = location.get('VOLUME')
        if volume is None:
            return None

        directory = location.get('DIR')
        if directory is None:
            return None

        file = location.get('FILE')
        if file is None:
            return None

        return volume + directory + file

    def remove_from_entry_element(self, name: str, mark_as_modified: bool = True) -> None:
        element = self._entry_element.find(name)
        if element is None:
            return

        self._entry_element.remove(element)

        if mark_as_modified:
            self._mark_as_modified_now()

    def get_from_entry_element(self, name: str) -> Optional[str]:
        return self._get_from_element(self._entry_element, name)

    def get_from_album_element(self, name: str) -> Optional[str]:
        return self._get_from_element(self._album_element, name)

    def get_from_info_element(self, name: str) -> Optional[str]:
        return self._get_from_element(self._info_element, name)

    def _set_in_element(self, element: ElementTree.Element, name: str, value: Optional[str],
                        mark_as_modified: bool = True) -> None:
        if value is None:
            element.attrib.pop(name)
        else:
            element.set(name, value)

        if mark_as_modified:
            self._mark_as_modified_now()

    def set_in_entry_element(self, name: str, value: Optional[str], mark_as_modified: bool = True) -> None:
        return self._set_in_element(self._entry_element, name, value, mark_as_modified)

    def set_in_album_element(self, name: str, value: Optional[str], mark_as_modified: bool = True) -> None:
        album_element = self._get_album_element(value is not None)
        return None if album_element is None else self._set_in_element(album_element, name, value, mark_as_modified)

    def set_in_info_element(self, name: str, value: Optional[str], mark_as_modified: bool = True) -> None:
        info_element = self._get_info_element(value is not None)
        return None if info_element is None else self._set_in_element(info_element, name, value, mark_as_modified)

    def flags(self) -> int:
        flags_value = self.get_from_info_element('FLAGS')
        return int(flags_value if flags_value is not None else 0)

    def set_flags(self, flags: int, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('FLAGS', str(flags))

        if mark_as_modified:
            self._mark_as_modified_now()

    def matches_filter(self, filtered_by: int) -> bool:
        if filtered_by == 0:
            return True
        elif filtered_by == Track.Filter.ONLY_TRACKS:
            return not self.is_a_stem() and not self.is_a_sample()
        elif filtered_by == Track.Filter.ONLY_STEMS:
            return self.is_a_stem()
        elif filtered_by == Track.Filter.ONLY_CLOUD_FILES:
            return self.is_a_cloud_file()
        else:
            return False

    def has_stems_version_generated(self) -> bool:
        return (self.flags() & 0x40) != 0

    def is_a_sample(self) -> bool:
        return self._entry_element.find('LOOPINFO') is not None

    def is_a_stem(self) -> bool:
        return self.has_stems_version_generated() or self._entry_element.find('STEMS') is not None

    def is_a_cloud_file(self) -> bool:
        location = self._entry_element.find('LOCATION')
        if location is None:
            return False

        return location.get('WEBADDRESS') is not None

    def file(self) -> Optional[Path]:
        if self.is_a_cloud_file():
            return None

        playlist_key = self.playlist_key()
        if playlist_key is None:
            return None

        return Path('/') / 'Volumes' / playlist_key.replace('/:', '/')

    def modification_date(self) -> Optional[datetime]:
        modified_date = self._entry_element.get('MODIFIED_DATE')
        if modified_date is None:
            return None
        date = Utility.date_from_string(modified_date, '%Y/%m/%d')
        if date is None:
            return None

        modified_time = self._entry_element.get('MODIFIED_TIME')
        if modified_time is None:
            return None
        seconds = Utility.string_to_int(modified_time)
        if seconds is None:
            return date

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        # -- Traktor modification dates are stored in UTC time.
        return Utility.utc_datetime(date.year, date.month, date.day, hour, minutes, seconds)

    def title(self) -> Optional[str]:
        return self._entry_element.get('TITLE')

    def set_title(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_entry_element('TITLE', value, mark_as_modified)

    def artist(self) -> Optional[str]:
        return self._entry_element.get('ARTIST')

    def set_artist(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_entry_element('ARTIST', value, mark_as_modified)

    def beatgrid_locked(self) -> bool:
        return self._entry_element.get('LOCK') == '1'

    def set_beat_grid_locked(self, value: bool, mark_as_modified: bool = True) -> None:
        string = '1' if value is True else '0'

        self.set_in_entry_element('LOCK', string, mark_as_modified)

        if mark_as_modified:
            self._mark_as_modified_now()

            date = Utility.utc_time_now()
            self._entry_element.set('LOCK_MODIFICATION_TIME', date.strftime('%Y-%m-%dT%H:%M:%S'))

    def beatgrid_lock_modified_date(self) -> Optional[datetime]:
        string = self._entry_element.get('LOCK_MODIFICATION_TIME')
        if string is None:
            return None

        return Utility.date_from_string(string, '%Y-%m-%dT%H:%M:%S', utc=True)

    def bitrate(self) -> Optional[int]:
        return Utility.string_to_int(self.get_from_info_element('BITRATE'))

    def set_bitrate(self, value: int, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('BITRATE', str(value), mark_as_modified)

    def genre(self) -> Optional[str]:
        return self.get_from_info_element('GENRE')

    def set_genre(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('GENRE', value, mark_as_modified)

    def label(self) -> Optional[str]:
        return self.get_from_info_element('LABEL')

    def set_label(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('LABEL', value, mark_as_modified)

    def producer(self) -> Optional[str]:
        return self.get_from_info_element('PRODUCER')

    def set_producer(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('PRODUCER', value, mark_as_modified)

    def mix(self) -> Optional[str]:
        return self.get_from_info_element('MIX')

    def set_mix(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('MIX', value, mark_as_modified)

    def release(self) -> Optional[str]:
        return self.get_from_album_element('TITLE')

    def set_release(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_album_element('TITLE', value, mark_as_modified)

    def track_number(self) -> Optional[int]:
        return Utility.string_to_int(self.get_from_album_element('TRACK'))

    def set_track_number(self, value: int, mark_as_modified: bool = True) -> None:
        self.set_in_album_element('TRACK', str(value), mark_as_modified)

    def comments(self) -> Optional[str]:
        return self.get_from_info_element('COMMENT')

    def set_comments(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('COMMENT', value, mark_as_modified)

    def comments2(self) -> Optional[str]:
        return self.get_from_info_element('RATING')

    def set_comments2(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('RATING', value, mark_as_modified)

    def remixer(self) -> Optional[str]:
        return self.get_from_info_element('REMIXER')

    def set_remixer(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('REMIXER', value, mark_as_modified)

    def key(self) -> Optional[str]:
        return self.get_from_info_element('KEY')

    def set_key(self, value: str, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('KEY', value, mark_as_modified)

    def play_count(self) -> Optional[int]:
        return Utility.string_to_int(self.get_from_info_element('PLAYCOUNT'))

    def set_play_count(self, value: int, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('PLAYCOUNT', str(value), mark_as_modified)

    def length(self) -> Optional[float]:
        return Utility.string_to_float(self.get_from_info_element('PLAYTIME_FLOAT'))

    def set_length(self, value: float, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('PLAYTIME', str(round(value)), mark_as_modified=False)
        self.set_in_info_element('PLAYTIME_FLOAT', '{:.06f}'.format(value), mark_as_modified)

    def rating(self) -> Optional[Rating]:
        # -- The following works with rekordbox and Serato too:
        # --    Unrated -> 0, 1-51 -> 1, 52-102 -> 2, 103-153 -> 3, 154-204 -> 4, 205-anything -> 5
        value = Utility.string_to_int(self.get_from_info_element('RANKING'))

        if value is None:
            return None

        if value == 0:
            return Rating.Unrated
        elif value < 52:
            return Rating.OneStar
        elif value < 103:
            return Rating.TwoStars
        elif value < 154:
            return Rating.ThreeStars
        elif value < 205:
            return Rating.FourStars
        elif value <= 255:
            return Rating.FiveStars

        return None

    def set_rating(self, value: Rating, mark_as_modified: bool = True) -> None:
        ratings_map = {
            Rating.Unrated: 0,
            Rating.OneStar: 51,
            Rating.TwoStars: 102,
            Rating.ThreeStars: 153,
            Rating.FourStars: 205,
            Rating.FiveStars: 255
        }

        self.set_in_info_element('RANKING', str(ratings_map[value]), mark_as_modified)

    def import_date(self) -> Optional[datetime]:
        return Utility.date_from_string(self.get_from_info_element('IMPORT_DATE'), '%Y/%m/%d')

    def set_import_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('IMPORT_DATE', value.strftime('%Y/%m/%d'), mark_as_modified)

    def last_played_date(self) -> Optional[datetime]:
        return Utility.date_from_string(self.get_from_info_element('LAST_PLAYED'), '%Y/%m/%d')

    def set_last_played_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('LAST_PLAYED', value.strftime('%Y/%m/%d'), mark_as_modified)

    def release_date(self) -> Optional[datetime]:
        return Utility.date_from_string(self.get_from_info_element('RELEASE_DATE'), '%Y/%m/%d')

    def set_release_date(self, value: datetime, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('RELEASE_DATE', value.strftime('%Y/%m/%d'), mark_as_modified)

    def file_size(self) -> Optional[int]:
        return Utility.string_to_int(self.get_from_info_element('FILESIZE'))

    def set_file_size(self, value: int, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('FILESIZE', str(value), mark_as_modified)

    def bpm(self) -> Optional[float]:
        tempo_element = self._entry_element.find('TEMPO')
        if tempo_element is None:
            return None

        return Utility.string_to_float(tempo_element.get('BPM'))

    def set_bpm(self, value: float, mark_as_modified: bool = True) -> None:
        tempo_element = self._entry_element.find('TEMPO')
        if tempo_element is None:
            tempo_element = ElementTree.SubElement(self._entry_element, 'TEMPO')

        tempo_element.set('BPM', '{:.06f}'.format(value))
        tempo_element.set('BPM_QUALITY', '100.000000')

        if mark_as_modified:
            self._mark_as_modified_now()

    def traktor_key(self) -> Optional[OpenNotation]:
        key_element = self._entry_element.find('MUSICAL_KEY')
        if key_element is None:
            return None

        value = Utility.string_to_int(key_element.get('VALUE'))
        if value is None:
            return None

        result: Optional[OpenNotation] = None

        try:
            result = OpenNotation(value)
        except ValueError:
            pass

        return result

    def set_traktor_key(self, value: OpenNotation, mark_as_modified: bool = True) -> None:
        key_element = self._entry_element.find('MUSICAL_KEY')
        if key_element is None:
            key_element = ElementTree.SubElement(self._entry_element, 'MUSICAL_KEY')

        key_element.set('VALUE', str(int(value)))

        if mark_as_modified:
            self._mark_as_modified_now()

    def color(self) -> Optional[Color]:
        value = Utility.string_to_int(self.get_from_info_element('COLOR'))
        if value is None:
            return None

        result: Optional[Color] = None

        try:
            result = Color(value)
        except ValueError:
            pass

        return result

    def set_color(self, value: Color, mark_as_modified: bool = True) -> None:
        self.set_in_info_element('COLOR', str(int(value)), mark_as_modified)

    def cover_art_image_from_file(self) -> Optional[PIL.Image.Image]:
        track_file = self.file()
        if track_file is None or not track_file.exists():
            return None

        # noinspection PyBroadException
        try:
            # -- Mutagen can automatically detect format and type of tags
            # -- Re: type ignore below, mutagen puts its public classes in private files
            # -- (https://github.com/quodlibet/mutagen/issues/647)
            file = mutagen.File(track_file)      # type: ignore[attr-defined]

            # -- Access APIC frame and grab the image
            tag = file.tags.get('APIC:', None)

            artwork_data: Optional[BytesIO] = None
            if tag is not None:
                artwork_data = BytesIO(tag.data)
            else:
                cover_list = file.get('covr', None)
                if cover_list is not None and len(cover_list) != 0:
                    # -- We only use the first cover from the list
                    artwork_data = BytesIO(cover_list[0])

            if artwork_data is None:
                return None

            return PIL.Image.open(artwork_data)
        except Exception:
            pass

        return None

    def cover_art_cache_file(self) -> Optional[Path]:
        if self._collection_folder is None:
            return None

        cover_art_id = self.get_from_info_element('COVERARTID')
        if cover_art_id is None:
            return None

        return self._collection_folder / 'CoverArt' / (cover_art_id + '000')

    def cover_art_image_from_cache(self) -> Optional[PIL.Image.Image]:
        database_image = self.cover_art_cache_file()
        if database_image is None or not database_image.exists():
            return None

        artwork_file = open(database_image, "rb")
        data = artwork_file.read()
        artwork_file.close()

        if data[0] != 8:
            return None

        width = ((data[4] << 24) | (data[3] << 16) | (data[2] << 8) | data[1])
        height = ((data[8] << 24) | (data[7] << 16) | (data[6] << 8) | data[5])
        rgba_data = bytearray()

        # -- Re-order the color components from little endian data.
        for pixel_index in range(0, width * height):
            data_index = 9 + (pixel_index * 4)

            rgba_data.append(data[data_index + 2])
            rgba_data.append(data[data_index + 1])
            rgba_data.append(data[data_index])
            rgba_data.append(data[data_index + 3])

        return PIL.Image.frombytes('RGBA', (width, height), bytes(rgba_data))

    def _hashed_file(self, infix: str, prefix: Optional[Path] = None) -> Optional[Path]:
        prefix = prefix or self._collection_folder
        if prefix is None:
            return None

        audio_id = self.get_from_entry_element('AUDIO_ID')
        if audio_id is None:
            return None

        return Path(prefix / infix / TraktorHash(audio_id).fullname)

    def stripe_file(self) -> Optional[Path]:
        return self._hashed_file('Stripes')

    def transients_file(self) -> Optional[Path]:
        return self._hashed_file('Transients')

    def generated_stems_file(self) -> Optional[Path]:
        # TODO: Read this from Collection.generatedStemsFolder()
        base_path = Path.home() / 'Music' / 'Traktor' / 'Stems'
        return self._hashed_file('', base_path)
