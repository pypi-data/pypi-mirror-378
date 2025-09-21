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

import os

from typing import List, Optional
from time import sleep
from pathlib import Path
from semver.version import VersionInfo

from PyUtilities import Utility
from PyUtilities.Exceptions import ArgumentError
from TraktorBuddy.NmlFile import NmlFile
from TraktorBuddy.Track import Track
from TraktorBuddy.Folder import Folder
from TraktorBuddy.Playlist import Playlist


# -- Classes
class Collection:
    """Interface for Traktor collection."""

    @classmethod
    def purge_backups(cls, test_mode: bool = False) -> None:
        backup_folder = Collection.traktor_collection_backup_folder()
        if backup_folder is None:
            return

        backup_list = os.listdir(backup_folder)
        nb_of_backups = len(backup_list)
        if nb_of_backups < 2:
            print('No backups to purge.')
            return

        if not test_mode:
            backup_list.sort()

            for file in backup_list[:-1]:
                (backup_folder / file).unlink()

        print('Purged ' + str(nb_of_backups - 1) + ' backup(s).')

    @classmethod
    def traktor_collection_backup_folder(cls) -> Optional[Path]:
        traktor_folder = Collection.latest_traktor_folder()
        if traktor_folder is None:
            return None

        return traktor_folder / 'Backup' / 'TraktorBuddy'

    @classmethod
    def native_instruments_folder(cls) -> Path:
        return Path.home() / 'Documents' / 'Native Instruments'

    @classmethod
    def latest_traktor_folder(cls) -> Optional[Path]:
        base_folder = Collection.native_instruments_folder()

        lastest_version: Optional[VersionInfo] = None

        for path in os.listdir(base_folder):
            if not path.startswith('Traktor '):
                continue

            try:
                version = VersionInfo.parse(path[8:])

                if version is not None:
                    if lastest_version is None or version > lastest_version:
                        lastest_version = version
            except ValueError:
                continue

        if lastest_version is None:
            return None

        return base_folder / ('Traktor ' + str(lastest_version))

    @classmethod
    def traktor_collection_file(cls) -> Optional[Path]:
        traktor_folder = Collection.latest_traktor_folder()
        if traktor_folder is None:
            return None

        return traktor_folder / 'collection.nml'

    @classmethod
    def generated_stems_folder(cls) -> Path:
        # TODO: Load settings.tsi and read Browser.Dir.GeneratedStems
        return Path.home() / 'Music' / 'Traktor' / 'Stems'

    def __init__(self, collection_file: Optional[Path] = None):
        """Constructor from a collection path, or it will just use the latest collection if no path is provided."""

        if collection_file is None:
            collection_file = Collection.traktor_collection_file()

            if collection_file is None:
                raise RuntimeError('Could not find any Traktor folder in "' +
                                   str(Collection.native_instruments_folder()) + '".')

        self._nml_file = NmlFile(nml_file=collection_file)
        self._root_folder: Optional[Folder] = None

        print('Parsing Traktor collection in "' + str(collection_file.parent) + '".')

    def folder(self) -> Optional[Path]:
        return self._nml_file.collection_folder()

    def make_backup(self) -> None:
        # -- Backups filename have a timestamp so we make sure to wait so that names cannot clash.
        sleep(1)

        backup_folder = Collection.traktor_collection_backup_folder()
        if backup_folder is None:
            return

        os.makedirs(backup_folder, exist_ok=True)

        arguments: List[str] = ['zip', '-j', Utility.utc_time_now().strftime('%Y-%m-%d-%H-%M-%S.zip'),
                                str(self._nml_file.collection_folder())]
        return_code, captured_output = Utility.shell_command(arguments, from_dir=backup_folder)
        if return_code != 0:
            raise RuntimeError('Error backing up collection.')

    def save(self) -> None:
        self.make_backup()

        self._nml_file.save()

        print('Saved Traktor collection in "' + str(self._nml_file.path()) + '".')

    def root_folder(self) -> Optional[Folder]:
        if self._root_folder is None:
            root_node = self._nml_file.root_folder_node()
            if root_node is None:
                return None

            self._root_folder = Folder(self._nml_file, root_node)

        return self._root_folder

    def find_all_tracks_at_path(self, path: str, filtered_by: int = 0) -> List[Track]:
        root_folder = self.root_folder()
        if root_folder is None:
            return []

        if path == '' or path == '/':
            return self.tracks(filtered_by)

        crate = root_folder.find(path.split('/'))
        if crate is None:
            raise RuntimeError('Could not find any folder or playlist at "' + path + '".')
        else:
            return crate.tracks(filtered_by)

    def tracks(self, filtered_by: int = 0) -> List[Track]:
        return self._nml_file.tracks(filtered_by)

    def number_of_tracks(self) -> int:
        return len(self._nml_file.tracks())

    def track_at_index(self, index: int) -> Track:
        if index >= self.number_of_tracks():
            raise ArgumentError('Out of bound access to a track.')

        return self._nml_file.tracks()[index]

    def track_with_playlist_key(self, key: str) -> Optional[Track]:
        return self._nml_file.track_with_playlist_key(key)

    def playlists_for_track(self, track: Track) -> List[Playlist]:
        root_folder = self.root_folder()
        if root_folder is None:
            return []

        return root_folder.playlists_for_track(track)

    def delete_track(self, track: Track) -> None:
        root_folder = self.root_folder()
        if root_folder is not None:
            for playlist in root_folder.playlists_for_track(track):
                playlist.delete_track(track)
