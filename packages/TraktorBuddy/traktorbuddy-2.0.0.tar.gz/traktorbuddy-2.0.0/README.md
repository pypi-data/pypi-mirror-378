# Traktor Buddy

[![GPL-v3.0](https://img.shields.io/badge/license-GPL--3.0-orange)](https://spdx.org/licenses/GPL-3.0-or-later.html) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/TraktorBuddy.svg)](https://python.org) [![PyPI - Version](https://img.shields.io/pypi/v/TraktorBuddy.svg)](https://pypi.org/project/TraktorBuddy)

A helping hand for managing **Traktor** collections.

### Installation

**Traktor Buddy** is a pure Python project. It requires at least [Python](https://python.org) 3.8.

You can install **Traktor Buddy** by typing the following in a terminal window:

```console
pip install TraktorBuddy
```

### Usage from the command line

**Traktor Buddy** supports various commands, sometimes with one or more extra arguments:

```console
tktbud <options> command <arguments> <path>
```

The following commands are supported:

```console
help <topic>       - Show a help message. topic is optional (use 'help topics' for a list).
version            - Print the current version.
tag <arguments>    - Add or remove tags (use 'help tag' for a list of arguments).
fix <arguments>    - Fix various things (use 'help fix' for a list of arguments).
purge              - Purge all collection backups apart from the most recent one.
listen             - Listen to tracks playing on Traktor and print info about them.
```

The following options are supported:

```console
--test/-t          - Run in test mode. Affected tracks are printed out. No changes are saved.
--debug/-d         - Enable extra debugging information.
--verbose/-c       - Enable verbose mode.
--only=filter      - Only apply commands to some type of tracks.
```

If `path` is provided then the action is only applied to the track contained in the Playlist/Folder at that path. Paths are `/` separated, i.e. `'/Folder1/Folder2/Playlist'`. Use `'\ '` for spaces. If no `path` is provided then then action is applied to **ALL** tracks in the collection.

### Always keep backups

**Traktor Buddy** creates a backup of your collection in the `Backup` folder of **Traktor** before modifying anything but it's best to have your own too just in case. Make sure to backup the entire **Traktor** folder, i.e. ` ~/Documents/Native Instruments/Traktor 3.11.1` on macOS for example.

Also, it's a good idea to run commands with the `-t` option first (which means test mode) to make sure you understand how many tracks are affected/modified (you can use verbose mode to print track information). Finally, it's also a good idea to test your command on a small playlist of tracks first before applying it to your entire collection.

### Tagging

Tags are words used to add custom properties or information to tracks. They can then be used to sort tracks more efficiently in smart playlists.

Tags are either single word, which describe a on/off type of value, or can use a `name:value` format which allows for sorting tracks based on a given value.

Most people will use playlists for sorting tracks in their collections but doing this requires manual upkeep. If you wanted to automatically sort your tracks based on, for example, the spot at which those tracks work in your set, you could add tags like `settime:early`,  `settime:late`, etc.. and create smart playlists in **Traktor** that automatically filter for `Comments2 contains settime:early`.

Another example is, since **Traktor** doesn't let you create smart playlists based on Playlist membership, you can tag all the tracks in a playlist and then create smart playlists to filter tracks that are in a given playlist and other criterias.

The possibilities are endless.

Tags are added to the `comments2` field in **Traktor**'s database. If you already have information in these fields it will not be deleted but the tag will be appended to it. If you delete a tag, it may also delete information that happens to use the same word. Be careful.

Most tagging commands are self-explanatory, allowing you to `add`, `delete` or `rename` a tag.

One slightly more obscure command is `tag years` which will automatically create a `Year` tag for all tracks that have a release date available. For example if a track was released on 3/5/2015 then the tag `Year:2015` will be added to the track if it's not already present.

This allows you to then easily sort tracks by year in smart playlists.

You can add the `--only` option to target only a certain type of tracks. `--only=tracks` will apply the tag only to regular tracks and not stem files while --only=stems` will apply the tag only to stem files.

### Fix commands

These commands can be used to fix things in your **Traktor** collection. Each command is very specific to one issue and only performs that one function.

##### fix labels

Some DJ software store record label information in the `grouping` field of the music file. If a track is missing its record label, this will look for it in the `grouping` field of the music file and if found will update the record label for that track.

##### fix itunes

This removes any `ITUNES` elements in the track's information. This element was used by **Traktor** to sync your tracks with your local iTunes collection.

##### fix coverart

If a track has a covert art cache entry in its information which does not exists anymore in **Traktor**'s cover art cache, this removes the cache entry information and touches (i.e. updates the modification date) the track's music file to force **Traktor** to reload the coverart from the file.

You can then simply load the track on a deck or check your database consistency and cover art will be read again and updated from the music file.

##### fix covercache

Goes thru **Traktor**'s cover art cache and deletes any file that is no longer being used by your track collection.

### Usage as a module

You can use **Traktor Buddy** in your own **Python** scripts to read and modify **Traktor** collections.

```
import TraktorBuddy

collection = TraktorBuddy.Collection()

for track in collection.tracks():
    print(track.title())
```

The module exposes classes for **Collection**, **Folder**, **Playlist**, **Track** or **Listener** for example. Full documentation will come later but the source code for those classes should make their interface fairly obvious.

### Listening to Traktor

You can use the `listen` command or the `Listener` class in the module to get updates on each Track that **Traktor** is playing.

For this to work on **Traktor**'s end you need to configure the broadcasting panel in settings:

* Set proxy server to `none`.
* Set server path to `localhost`.
* Set the port to `8000`.
* Set the mount path to `/`.
* Leave the password empty.
* Select the lowest frequency and bitrate for format since we won't be using the audio.

Now start `tktbud` or your own app in listening mode and then turn **Traktor**'s broadcasting on in the audio recorder panel (the little antenna). If everything works correctly the blue broadcasting light should stay on and you are ready to receive updates.

**Traktor** sends a new track update when a track is marked as played. This length of time before this happen can be set via the `Play Count` setting in the transport section of the settings,

### License

**Traktor Buddy** is distributed under the terms of the [GPLv3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or later license.
