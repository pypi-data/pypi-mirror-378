#
# Copyright (c) 2022-present Didier Malenfant <didier@malenfant.net>
#
# This file is part of
#
# TraktorBuddy is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TraktorBuddy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with  If not,
# see <https://www.gnu.org/licenses/>.
#

import getopt
import sys
import traceback
import time
import mutagen

from typing import List, Dict, Callable
from pathlib import Path
from dataclasses import dataclass

from PyUtilities import Utility
from PyUtilities.Exceptions import ArgumentError
from TraktorBuddy.__about__ import __appname__
from TraktorBuddy.__about__ import __version__
from TraktorBuddy.Collection import Collection
from TraktorBuddy.Track import Track
from TraktorBuddy.Listener import Listener


_test_mode = False
_verbose_mode = False
_track_filter = 0


def _new_track_posted(track: Track) -> None:
    label = track.label()
    if label is None:
        print(f'Playing "{track.title()}" by {track.artist()}.')
    else:
        print(f'Playing "{track.title()}" by {track.artist()} [{label}].')


def fix(commands: List[str]) -> None:
    @dataclass
    class FixSubCommand:
        func: Callable[[Collection, List[Track]], None]
        min_nb_of_commands: int
        max_nb_of_commands: int

    switch: Dict[str, FixSubCommand] = {
        'labels': FixSubCommand(fix_labels, 2, 3),
        'itunes': FixSubCommand(fix_itunes, 2, 3),
        'coverart': FixSubCommand(fix_cover_art, 2, 3),
        'covercache': FixSubCommand(fix_cover_cache, 2, 2),
        'cloudfiles': FixSubCommand(fix_cloud_files, 2, 2)
    }

    sub_command_name = commands[1]
    sub_command = switch.get(sub_command_name)
    if sub_command is None:
        raise ArgumentError(f'Unknown argument "{sub_command_name}" to "fix" command.')

    nb_of_commands = len(commands)
    if nb_of_commands < sub_command.min_nb_of_commands:
        raise ArgumentError('Expected an argument to "fix" command.')
    elif nb_of_commands > sub_command.max_nb_of_commands:
        raise ArgumentError('Too many arguments to "fix" command.')

    collection = Collection()
    tracks = collection.tracks() if nb_of_commands == sub_command.min_nb_of_commands else (
        collection.find_all_tracks_at_path(commands[sub_command.min_nb_of_commands]))
    sub_command.func(collection, tracks)


def fix_labels(collection: Collection, tracks: List[Track]) -> None:
    nb_of_tracks_checked = 0
    nb_of_tracks_with_no_labels = 0
    nb_of_tracks_fixed = 0

    for track in tracks:
        if track.is_a_sample():
            continue

        nb_of_tracks_checked += 1

        if track.label() is not None and track.label() != '':
            continue

        nb_of_tracks_with_no_labels += 1

        file = track.file()
        if file is None or not file.exists():
            continue

        # -- Re: type ignore below, mutagen puts its public classes in private files
        # -- (https://github.com/quodlibet/mutagen/issues/647)
        file_data = mutagen.File(track.file())      # type: ignore[attr-defined]
        if file_data.tags is None:
            continue

        grouping = file_data.tags.get('©grp')
        if grouping is not None:
            if len(grouping) > 0 and grouping[0] != '':
                if not _test_mode:
                    track.set_label(grouping[0])

                if _verbose_mode:
                    print(track.file())
                    print(f'(found {grouping[0]} instead of {track.label()}).')

                nb_of_tracks_fixed += 1
        '''
        else:
            printed_file_path: bool = False

            for tag in file_data.tags:
                if tag.startswith('APIC') or tag.startswith('PRIV:') or tag.startswith('GEOB:') or
                   tag.startswith('POPM:') or tag.startswith('covr'):
                    continue
                if tag.startswith('©too'):
                    continue
                if tag.startswith('disk'):
                    continue
                if tag.startswith('©day'):
                    continue
                if tag.startswith('©nam'):
                    continue
                if tag.startswith('©alb'):
                    continue
                if tag.startswith('©ART'):
                    continue
                if tag.startswith('©gen'):
                    continue
                if tag.startswith('tmpo'):
                    continue
                if tag.startswith('----:com.apple.iTunes:initialkey'):
                    continue
                if tag.startswith('----:com.apple.iTunes:rating wmp'):
                    continue
                if tag.startswith('cpil'):
                    continue
                if tag.startswith('©cmt'):
                    continue
                if tag.startswith('TSSE'):
                    continue
                if tag.startswith('TPE1'):
                    continue
                if tag.startswith('TCMP'):
                    continue
                if tag.startswith('TIT2'):
                    continue
                if tag.startswith('TCON'):
                    continue
                if tag.startswith('TKEY'):
                    continue
                if tag.startswith('COMM::eng'):
                    continue
                if tag.startswith('TDRC'):
                    continue
                if tag.startswith('TBPM'):
                    continue
                if tag.startswith('TDOR'):
                    continue
                if tag.startswith('TDRL'):
                    continue
                if tag.startswith('TPE4'):
                    continue
                if tag.startswith('TENC'):
                    continue
                if tag.startswith('©wrt'):
                    continue
                if tag.startswith('trkn'):
                    continue
                if tag.startswith('TLEN'):
                    continue
                if tag.startswith('TXXX'):
                    continue
                if tag.startswith('TALB'):
                    continue
                if tag.startswith('TXXX'):
                    continue
                if tag.startswith('TRCK'):
                    continue
                if tag.startswith('aART'):
                    continue
                if tag.startswith('RVA2:SeratoGain'):
                    continue
                if tag.startswith('COMM:ID3v1 Comment'):
                    continue
                if tag.startswith('TSOT'):
                    continue
                if tag.startswith('TSOA'):
                    continue
                if tag.startswith('----:com.apple.iTunes:energylevel'):
                    continue
                if tag.startswith('----:com.apple.iTunes:iTunNORM'):
                    continue
                if tag.startswith('----:com.apple.iTunes:iTunSMPB'):
                    continue
                if tag.startswith('apID'):
                    continue
                if tag.startswith('cnID'):
                    continue
                if tag.startswith('ownr'):
                    continue
                if tag.startswith('plID'):
                    continue
                if tag.startswith('purd'):
                    continue
                if tag.startswith('stik'):
                    continue
                if tag.startswith('----:com.apple.iTunes:iTunMOVI'):
                    continue
                if tag.startswith('sonm'):
                    continue
                if tag.startswith('COMM:iTunSMPB:eng'):
                    continue
                if tag.startswith('COMM:iTunNORM:eng'):
                    continue
                if tag.startswith('TPOS'):
                    continue
                if tag.startswith('atID'):
                    continue
                if tag.startswith('geID'):
                    continue
                if tag.startswith('soal'):
                    continue
                if tag.startswith('soar'):
                    continue
                if tag.startswith('soco'):
                    continue
                if tag.startswith('----:com.apple.iTunes:Encoding Params'):
                    continue
                if tag.startswith('UFID:https://www.jhutveckling.se'):
                    continue
                if tag.startswith('GRP1'):
                    continue
                if tag.startswith('TIT1'):
                    continue
                if tag.startswith('rtng'):
                    continue
                if tag.startswith('cprt'):
                    continue
                if tag.startswith('sfID'):
                    continue
                if tag.startswith('xid '):
                    continue
                if tag.startswith('cmID'):
                    continue
                if tag.startswith('pgap'):
                    continue
                if tag.startswith('----:com.apple.iTunes:iTunes_CDDB_TrackNumber'):
                    continue

                if _verbose_mode is True:
                    if printed_file_path is False:
                        printed_file_path = True
                        print(track.file())

                    # -- This is a debug test to print unknown tags
                    print(f'{tag}: {file_data.tags[tag]}')
        '''

    if _test_mode:
        print(f'Checked {nb_of_tracks_checked} tracks. {nb_of_tracks_with_no_labels} with no labels. '
              f'{nb_of_tracks_fixed} of them can be fixed.')
    else:
        print(f'Checked {nb_of_tracks_checked} tracks. {nb_of_tracks_with_no_labels} with no labels. Fixed '
              f'{nb_of_tracks_fixed} of them.')

    if _test_mode is False and nb_of_tracks_fixed > 0:
        collection.save()


def fix_itunes(collection: Collection, tracks: List[Track]) -> None:
    nb_of_tracks_checked = 0
    nb_of_tracks_with_itunes_info = 0

    for track in tracks:
        if track.is_a_sample():
            continue

        nb_of_tracks_checked += 1

        if track.get_from_entry_element('ITUNES') is not None:
            continue

        nb_of_tracks_with_itunes_info += 1

        if _verbose_mode:
            print(track.file())

        if not _test_mode:
            track.remove_from_entry_element('ITUNES')

    if _test_mode:
        print(f'Checked {nb_of_tracks_checked} tracks. {nb_of_tracks_with_itunes_info} with iTunes info tags.')
    else:
        print(f'Checked {nb_of_tracks_checked} tracks. Removed iTunes info tags from '
              f'{nb_of_tracks_with_itunes_info} of them.')

    if _test_mode is False and nb_of_tracks_with_itunes_info > 0:
        collection.save()


def fix_cover_art(collection: Collection, tracks: List[Track]) -> None:
    nb_of_tracks_checked = 0
    nb_of_tracks_with_missing_coverart_in_cache = 0
    track_files_to_touch: List[Path] = []

    collection_folder = collection.folder()
    if collection_folder is None:
        return

    for track in tracks:
        if track.is_a_sample():
            continue

        nb_of_tracks_checked += 1

        cache_image = track.cover_art_cache_file()
        if cache_image is not None and cache_image.exists():
            continue

        if cache_image is None:
            file_coverart_image = track.cover_art_image_from_file()
            if file_coverart_image is None:
                continue

            file_coverart_image.close()

        nb_of_tracks_with_missing_coverart_in_cache += 1

        track_file = track.file()
        if track_file is None:
            continue

        if _verbose_mode:
            print(track_file)

        if track_file.exists():
            track_files_to_touch.append(track_file)

        if not _test_mode:
            if cache_image is not None:
                track.set_in_info_element('COVERARTID', None)

    if _test_mode:
        print(f'Checked {nb_of_tracks_checked} tracks. {nb_of_tracks_with_missing_coverart_in_cache} with missing or '
              f'invalid cache coverart.')
    else:
        print(f'Checked {nb_of_tracks_checked} tracks. Removed invalid coverart ID from '
              f'{nb_of_tracks_with_missing_coverart_in_cache} of them.')

    if _test_mode is False and nb_of_tracks_with_missing_coverart_in_cache > 0:
        collection.save()

        # -- We need Traktor to spot that the track file is newer than the date in the collection
        time.sleep(5)

        for path in track_files_to_touch:
            path.touch()


def fix_cover_cache(collection: Collection, tracks: List[Track]) -> None:
    collection_folder = collection.folder()
    if collection_folder is None:
        return

    cache_folder = collection_folder / 'CoverArt'
    cache_files_found: Dict[str, bool] = {}

    nb_of_cache_entries = 0
    nb_of_orphan_cache_entries = 0

    for track in tracks:
        cache_file = track.cover_art_cache_file()
        if cache_file is None:
            continue

        cache_files_found[str(cache_file.relative_to(cache_folder))[:-3]] = True

        nb_of_cache_entries += 1

    for p in cache_folder.rglob('*'):
        if not p.is_dir():
            continue

        for m in p.rglob('*'):
            if m.is_dir():
                continue

            cache_file_as_string = str(m.relative_to(cache_folder))[:-3]
            if cache_file_as_string in cache_files_found:
                continue

            nb_of_orphan_cache_entries += 1

            if _verbose_mode:
                print(str(m.relative_to(cache_folder)))

            if not _test_mode:
                m.unlink()

    if _test_mode:
        print(f'Checked coverart {nb_of_cache_entries} cache entries. {nb_of_orphan_cache_entries} of wich are '
              f'orphans.')
    else:
        print(f'Checked {nb_of_cache_entries} tracks. Deleted {nb_of_orphan_cache_entries} orphans coverart cache '
              f'entries.')


def fix_cloud_files(collection: Collection, tracks: List[Track]) -> None:
    collection_folder = collection.folder()
    if collection_folder is None:
        return

    nb_of_cloud_files = 0
    nb_of_orphan_cloud_files = 0
    nb_of_tracks = 0

    print('Looking for orphan cloud tracks. This might take a while if you have a lot of folders/playlists in '
          'your collections.')
    for track in tracks:
        if track.is_a_cloud_file():
            nb_of_cloud_files += 1

            if len(collection.playlists_for_track(track)) == 0:
                nb_of_orphan_cloud_files += 1

        nb_of_tracks += 1

    if _test_mode:
        print(f'Checked {nb_of_tracks} tracks. {nb_of_cloud_files} of wich are cloud files and '
              f'{nb_of_orphan_cloud_files} of wich are orphans.')
    else:
        print(f'Checked {nb_of_tracks} tracks. Deleted {nb_of_orphan_cloud_files} orphan cloud files.')


def tag(commands: List[str]) -> None:
    if len(commands) < 2:
        raise ArgumentError('Expected an argument to "tag" command.')

    switch: Dict[str, Callable[[List[str]], None]] = {
        'add': add_tag,
        'remove': remove_tag,
        'rename': rename_tag,
        'years': add_year_tag
    }

    sub_command = commands[1]
    method = switch.get(sub_command)
    if method is None:
        raise ArgumentError('Unknown argument "' + sub_command + '" to "tag" command.')

    method(commands)


def add_tag(commands: List[str]) -> None:
    nb_of_commands = len(commands)
    if nb_of_commands > 4:
        raise ArgumentError('Too many arguments to "add" command.')
    elif nb_of_commands < 3:
        raise ArgumentError('Expected name argument to "add" command.')

    # noinspection DuplicatedCode
    tag_name = commands[2]
    if tag_name.__contains__(' '):
        raise ArgumentError('Tag names should not contain spaces.')

    collection = Collection()
    tracks = collection.tracks(_track_filter) if nb_of_commands == 3 else (
        collection.find_all_tracks_at_path(commands[3], _track_filter))

    nb_of_tracks_tagged = 0
    for track in tracks:
        if track.is_a_sample():
            continue

        existing_value = track.comments2()
        if existing_value is None:
            existing_value = tag_name
        elif tag_name in existing_value.split(' '):
            continue
        else:
            existing_value += ' ' + tag_name

        track.set_comments2(existing_value)
        nb_of_tracks_tagged += 1

        if _verbose_mode:
            print(track.file())

    print('Tagged ' + str(nb_of_tracks_tagged) + ' tracks.')
    if _test_mode is False and nb_of_tracks_tagged > 0:
        collection.save()


def remove_tag(commands: List[str]) -> None:
    nb_of_commands = len(commands)
    if nb_of_commands > 4:
        raise ArgumentError('Too many arguments to "remove" command.')
    elif nb_of_commands < 3:
        raise ArgumentError('Expected name argument to "remove" command.')

    # noinspection DuplicatedCode
    tag_name = commands[2]
    if tag_name.__contains__(' '):
        raise ArgumentError('Tag names should not contain spaces.')

    collection = Collection()
    tracks = collection.tracks(_track_filter) if nb_of_commands == 3 else (
        collection.find_all_tracks_at_path(commands[3], _track_filter))

    nb_of_tracks_tagged = 0
    for track in tracks:
        if track.is_a_sample():
            continue

        existing_value = track.comments2()
        if existing_value is None:
            continue

        names = existing_value.split(' ')
        if tag_name not in names:
            continue

        names.remove(tag_name)
        track.set_comments2(' '.join(names))
        nb_of_tracks_tagged += 1

        if _verbose_mode:
            print(track.file())

    print('Removed tag from ' + str(nb_of_tracks_tagged) + ' tracks.')
    if _test_mode is False and nb_of_tracks_tagged > 0:
        collection.save()


def rename_tag(commands: List[str]) -> None:
    nb_of_commands = len(commands)
    if nb_of_commands > 5:
        raise ArgumentError('Too many arguments to "rename" command.')
    elif nb_of_commands < 4:
        raise ArgumentError('Expected old and new name arguments to "rename" command.')

    old_tag_name = commands[2]
    if old_tag_name.__contains__(' '):
        raise ArgumentError('Tag names should not contain spaces.')

    new_tag_name = commands[3]
    if new_tag_name.__contains__(' '):
        raise ArgumentError('Tag names should not contain spaces.')

    collection = Collection()
    tracks = collection.tracks(_track_filter) if nb_of_commands == 4 else (
        collection.find_all_tracks_at_path(commands[4], _track_filter))

    nb_of_tracks_tagged = 0
    for track in tracks:
        if track.is_a_sample():
            continue

        existing_value = track.comments2()
        if existing_value is None:
            continue

        names = existing_value.split(' ')
        if old_tag_name not in names:
            continue

        names.remove(old_tag_name)
        track.set_comments2(' '.join(names) + ' ' + new_tag_name)
        nb_of_tracks_tagged += 1

        if _verbose_mode:
            print(track.file())

    print('Renamed tag in ' + str(nb_of_tracks_tagged) + ' tracks.')
    if _test_mode is False and nb_of_tracks_tagged > 0:
        collection.save()


def add_year_tag(commands: List[str]) -> None:
    nb_of_commands = len(commands)
    if nb_of_commands > 4:
        raise ArgumentError('Too many arguments to "years" command.')
    elif nb_of_commands < 3:
        raise ArgumentError('Expected old and new name arguments to "rename" command.')

    collection = Collection()
    tracks = collection.tracks(_track_filter) if nb_of_commands == 3 else (
        collection.find_all_tracks_at_path(commands[3], _track_filter))

    nb_of_tracks_tagged = 0
    for track in tracks:
        if track.is_a_sample():
            continue

        release_date = track.release_date()
        if release_date is None:
            continue

        year = release_date.year
        if year == 0:
            continue

        tag_name = 'Year:' + str(year)

        existing_value = track.comments2()
        if existing_value is None:
            existing_value = tag_name
        elif tag_name in existing_value.split(' '):
            continue
        else:
            existing_value += ' ' + tag_name

        if _test_mode:
            track.set_comments2(existing_value)

        nb_of_tracks_tagged += 1

        if _verbose_mode:
            print(track.file())

    print('Tagged ' + str(nb_of_tracks_tagged) + ' tracks.')
    if _test_mode is False and nb_of_tracks_tagged > 0:
        collection.save()


def purge_backups(_commands: List[str]) -> None:
    Collection.purge_backups(test_mode=_test_mode)


def listen(commands: List[str]) -> None:
    nb_of_commands = len(commands)
    if nb_of_commands > 2:
        raise ArgumentError('Too many arguments to "listen" command.')

    print('Listening to Traktor... (press CTRL-C to quit)')
    listener = Listener(Collection(), _new_track_posted)
    listener.start()


def print_usage(commands: List[str]) -> None:
    if len(commands) > 1:
        switch: Dict[str, Callable[[List[str]], None]] = {
            'topics': print_topics,
            'tag': print_tag_usage,
            'fix': print_fix_usage,
            'license': print_license,
            'only': print_only_help
        }

        method = switch.get(commands[1])
        if method is None:
            raise ArgumentError('Unknown topic "' + commands[1] + '".')

        method(commands)
        return

    print_version(commands)
    print('')
    print('usage: tktbud <options> <command> <arguments> <path>')
    print('')
    print('The following commands are supported:')
    print('')
    print('   help <topic>       - Show a help message. topic is optional (use "help topics" for a list).')
    print('   version            - Print the current version.')
    print('   tag <arguments>    - Add or remove tags (use "help tag" for a list of arguments).')
    print('   fix <arguments>    - Fix various things (use "help fix" for a list of arguments).')
    print('   purge              - Purge all collection backups apart from the most recent one.')
    print('   listen             - Listen to tracks playing on Traktor and print info about them.')
    print('')
    print('The following options are supported:')
    print('')
    print('   --test/-t          - Run in test mode. Affected tracks are printed out. No changes are saved.')
    print('   --debug/-d         - Enable extra debugging information.')
    print('   --verbose/-v       - Enable verbose mode (prints information on the tracks affected).')
    print('   --only=filter      - Only apply commands to some type of tracks (see help filter for more information)')
    print('')
    print('If path is provided then the action is only applied to the track contained in the Playlist/Folder at that '
          'path. Paths are / separated, i.e. "/Folder1/Folder2/Playlist". Use "\\ " for spaces.')
    print('')
    print('If no path is provided the action is applied to ALL tracks in the collection.')
    print('')
    print('TraktorBuddy is free software, type "tktbud help license" for license information.')


def print_version(_commands: List[str]) -> None:
    print('🎧 Traktor Buddy v' + __version__ + ' 🎧')


def print_topics(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   tktbud help tag     - List arguments accepted by the tag command.')
    print('   tktbud help fix     - List arguments accepted by the fix command.')
    print('   tktbud help license - Show the license for the app.')
    print('   tktbud help filter  - Display helps about the argument to the --only option.')
    print('')


def print_tag_usage(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   tktbud tag add <name> <path>          - Add a tag named "name" to all tracks in "path".')
    print('   tktbud tag delete <name> <path>       - Delete a tag named "name" for all tracks in "path".')
    print('   tktbud tag rename <old> <new> <path>  - Rename tags named "old" to "new" for tracks in "path".')
    print('   tktbud tag years <path>               - Add track\'s release year as a tag (i.e. Year:2022).')
    print('')


def print_fix_usage(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   tktbud fix labels <path>   - Grab missing record labels from the track file\'s grouping field for all '
          'tracks in "path".')
    print('   tktbud fix itunes <path>   - Delete iTunes info, if present, for all tracks in "path".')
    print('   tktbud fix coverart <path> - Force Traktor to reload the coverart if the cached file is missing for all '
          'tracks in "path".')
    print('   tktbud fix covercache      - Remove any files in the coverart cache that is not used by any tracks in '
          'the collection.')
    print('')


def print_only_help(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('Usage:')
    print('   tktbud --only=tracks ...         - Only apply command to regular tracks.')
    print('   tktbud --only=stems ...          - Only apply command to stem files.')
    print('')


def print_license(commands: List[str]) -> None:
    print_version(commands)
    print('')
    print('GPL License Version 3')
    print('')
    print('Copyright (c) 2024-present Didier Malenfant <didier@malenfant.net>')
    print('')
    print('TraktorBuddy is free software: you can redistribute it and/or modify it under the terms of the GNU General')
    print('Public License as published by the Free Software Foundation, either version 3 of the License, or')
    print('(at your option) any later version.')
    print('')
    print('TraktorBuddy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the')
    print('implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public')
    print('License for more details.')
    print('')
    print('You should have received a copy of the GNU General Public License along with TraktorBuddy. If not,')
    print('see <https://www.gnu.org/licenses/>.')
    print('')


def main() -> None:
    global _test_mode
    global _verbose_mode
    global _track_filter

    debug_on = False

    Utility.set_app_info(__appname__, __version__)

    try:
        # -- Gather the arguments, remove the first argument (which is the script filename)
        opts, commands = getopt.getopt(sys.argv[1:], 'tdv', ['help', 'test', 'debug', 'verbose', 'only='])

        for o, a in opts:
            if o in ('-t', '--test'):
                print('Running in test mode.')
                _test_mode = True
            elif o in ('-d', '--debug'):
                print('Enabling debugging information.')
                debug_on = True
            elif o in ('-v', '--verbose'):
                print('Enabling verbose mode.')
                _verbose_mode = True
            elif o in '--only':
                if a == 'tracks':
                    _track_filter = Track.Filter.ONLY_TRACKS
                elif a == 'stems':
                    _track_filter = Track.Filter.ONLY_STEMS
                else:
                    raise ArgumentError(f'Invalid filter "{filter}".')
            elif o in '--help':
                commands = ['help']

        if len(commands) == 0:
            raise ArgumentError('Expected a command! Maybe start with `tktbud help`?')

        switch: Dict[str, Callable[[List[str]], None]] = {
            'help': print_usage,
            'version': print_version,
            'tag': tag,
            'purge': purge_backups,
            'fix': fix,
            'listen': listen
        }

        if commands is None:
            raise ArgumentError('Expected a command! Maybe start with `tktbud help`?')

        command = commands[0]
        method = switch.get(command)
        if method is None:
            raise ArgumentError('Unknown commanwd "' + command + '".')

        if (_test_mode is not True and command != 'help' and command != 'version' and command != 'listen' and
                Utility.process_is_running('Traktor')):
            raise RuntimeError('Traktor seems to be running. It is not a good idea to make changes to the'
                               'collection at this time.')

        method(commands)

    except getopt.GetoptError:
        print_usage([])
    except Exception as e:
        if debug_on:
            print(traceback.format_exc())
        else:
            print(f'Error: {e}')

        sys.exit(1)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        pass


if __name__ == '__main__':
    main()
