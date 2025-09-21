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

from typing import List, Optional

from TraktorBuddy.Track import Track
from TraktorBuddy.NmlFile import NmlFile


# -- Class
class Playlist:
    """Interface for Traktor playlists."""

    def __init__(self, nml_file: NmlFile, node_element: ElementTree.Element):
        """Constructor from an XML entry element."""

        self._node_element = node_element
        self._nml_file = nml_file
        self._tracks: Optional[List[Track]] = None

    def name(self) -> Optional[str]:
        return self._node_element.get('NAME')

    def tracks(self, filtered_by: int = 0) -> List[Track]:
        if self._tracks is not None:
            if filtered_by == 0:
                return self._tracks

            result: List[Track] = []

            for track in self._tracks:
                if track.matches_filter(filtered_by):
                    result.append(track)

            return result

        self._tracks = []

        playlist_element = self._node_element.find('PLAYLIST')
        if playlist_element is None:
            return self._tracks

        if playlist_element.get('TYPE') != 'LIST':
            return self._tracks

        for entry in playlist_element.findall('ENTRY'):
            primary_key = entry.find('PRIMARYKEY')
            if primary_key is None:
                continue

            entry_type = primary_key.get('TYPE')
            if entry_type != 'TRACK' and entry_type != 'STEM':
                continue

            key = primary_key.get('KEY')
            if key is None:
                continue

            track_found = self._nml_file.track_with_playlist_key(key)
            if track_found is None:
                continue

            if filtered_by != 0 and not track_found.matches_filter(filtered_by):
                continue

            self._tracks.append(track_found)

        return self._tracks

    def contains_track(self, track: Track) -> bool:
        for other_track in self.tracks():
            if other_track.playlist_key() == track.playlist_key():
                return True

        return False

    def delete_track(self, track: Track) -> None:
        new_tracks_after_delete: List[Track] = []

        for other_track in self.tracks():
            if other_track.playlist_key() != track.playlist_key():
                new_tracks_after_delete.append(other_track)

        self._tracks = new_tracks_after_delete
