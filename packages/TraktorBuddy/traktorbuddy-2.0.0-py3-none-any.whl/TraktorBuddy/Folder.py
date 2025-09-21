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

from __future__ import annotations

import xml.etree.ElementTree as ElementTree

from typing import List, Optional

from TraktorBuddy.NmlFile import NmlFile
from TraktorBuddy.Playlist import Playlist
from TraktorBuddy.Track import Track


# -- Class
class Folder:
    """Interface for Traktor folders."""

    def __init__(self, nml_file: NmlFile, node_element: ElementTree.Element):
        """Constructor from an XML entry element."""

        self._node_element = node_element
        self._nml_file = nml_file
        self._folders: Optional[List[Folder]] = None
        self._playlists: Optional[List[Playlist]] = None

    def playlists_for_track(self, track: Track) -> List[Playlist]:
        results: List[Playlist] = []

        for folder in self.folders():
            results += folder.playlists_for_track(track)

        for playlist in self.playlists():
            if playlist.contains_track(track):
                results.append(playlist)

        return results

    def name(self) -> Optional[str]:
        return self._node_element.get('NAME')

    def find(self, names: List[str]) -> Optional[Folder | Playlist]:
        name = names[0]
        nb_of_names = len(names)

        for playlist in self.playlists():
            if playlist.name() == name:
                if nb_of_names == 1:
                    return playlist

        for folder in self.folders():
            if folder.name() == name:
                if nb_of_names == 1:
                    return folder
                else:
                    return folder.find(names[1:])

        return None

    def find_folder(self, names: List[str]) -> Optional[Folder | Playlist]:
        result = self.find(names)
        if not isinstance(result, Folder):
            return None

        return result

    def find_playlist(self, names: List[str]) -> Optional[Folder | Playlist]:
        result = self.find(names)
        if not isinstance(result, Playlist):
            return None

        return result

    def folders(self) -> List['Folder']:
        if self._folders is not None:
            return self._folders

        self._folders = []

        subnodes = self._node_element.find('SUBNODES')
        if subnodes is None:
            return self._folders

        for node in subnodes.findall('NODE'):
            if node.get('TYPE') != 'FOLDER':
                continue

            self._folders.append(Folder(self._nml_file, node))

        return self._folders

    def playlists(self) -> List[Playlist]:
        if self._playlists is not None:
            return self._playlists

        self._playlists = []

        subnodes = self._node_element.find('SUBNODES')
        if subnodes is None:
            return self._playlists

        for node in subnodes.findall('NODE'):
            if node.get('TYPE') != 'PLAYLIST':
                continue

            self._playlists.append(Playlist(self._nml_file, node))

        return self._playlists

    def tracks(self, filtered_by: int = 0) -> List[Track]:
        result: List[Track] = []

        for folder in self.folders():
            result = result + folder.tracks(filtered_by)

        for playlist in self.playlists():
            result = result + playlist.tracks(filtered_by)

        return result
