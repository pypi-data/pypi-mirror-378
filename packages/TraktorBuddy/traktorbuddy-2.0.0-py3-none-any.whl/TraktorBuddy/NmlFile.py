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
from pathlib import Path

from PyUtilities import Utility
from PyUtilities.Exceptions import ArgumentError
from TraktorBuddy.Track import Track


# -- Classes
class NmlFile:
    """Interface for Traktor's NML files."""

    def __init__(self, nml_file: Optional[Path] = None, collection_folder: Optional[Path] = None,
                 _mock_element: Optional[ElementTree.Element] = None):
        """Constructor from a file path."""

        self._nml_file = nml_file

        if _mock_element is None:
            if self._nml_file is None:
                raise RuntimeError('Real NML files require a collection file path.')

            self._collection_folder = self._nml_file.parent
            nml_element = ElementTree.ElementTree(file=self._nml_file).getroot()

            if nml_element is None:
                raise RuntimeError(f'NML file "{nml_file} is malformed.')

            self._nml_element = nml_element
        else:
            if collection_folder is None:
                raise RuntimeError('Mock NML files require a collection folder path.')

            self._collection_folder = collection_folder
            self._nml_element = _mock_element

        self._tracks: Optional[List[Track]] = None

    def path(self) -> Path:
        if self._nml_file is None:
            raise RuntimeError('Cannot return path to NML mock files.')

        return self._nml_file

    def collection_folder(self) -> Path:
        return self._collection_folder

    def save(self) -> None:
        if self._nml_file is None:
            raise RuntimeError('Cannot save NML mock files.')

        with open(self._nml_file, 'w') as out_file:
            out_file.write(Utility.xml_element_to_string(self._nml_element, xml_declaration=True))

    def root_folder_node(self) -> Optional[ElementTree.Element]:
        nml_element = self._nml_element
        if nml_element is None:
            raise RuntimeError('Invalid collection object.')

        playlists_element = nml_element.find('PLAYLISTS')
        if playlists_element is None:
            return None

        return playlists_element.find('NODE')

    def tracks(self, filtered_by: int = 0) -> List[Track]:
        if self._tracks is not None:
            return self._tracks

        self._tracks = []

        collection_element = self._nml_element.find('COLLECTION')
        if collection_element is None:
            return self._tracks

        for entry in collection_element.findall('ENTRY'):
            track = Track(entry, self._collection_folder)

            if track.file() is None and not track.is_a_cloud_file():
                continue

            if filtered_by != 0 and not track.matches_filter(filtered_by):
                continue

            self._tracks.append(track)

        return self._tracks

    def track_with_playlist_key(self, key: str) -> Optional[Track]:
        for track in self.tracks():
            if track.playlist_key() == key:
                return track

        return None

    def number_of_tracks(self) -> int:
        return len(self.tracks())

    def track_at_index(self, index: int) -> Track:
        if index >= self.number_of_tracks():
            raise ArgumentError('Out of bound access to a track.')

        return self.tracks()[index]
