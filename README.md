
# Synophotos CLI

Synophotos Command Line Interface (CLI) is an attempt to enable remote control of certain functions in Synology Photos from a terminal.

## Features

- connect to a Synology Photos instance and run various commands remotely 
- list and count albums, folders and images
- list users and groups
- create albums and populate albums from existing items
- share and unshare albums

### `count`

```
Usage: synophotos count [OPTIONS] [PARENT_ID]

  counts various things

Options:
  -a, --albums   counts the number of albums
  -f, --folders  counts the number of folders
  -i, --items    counts the number of items
  --help         Show this message and exit.
```

### `create`

Creates an album with the provided name. By default, the album is empty, but can be populated with images from
a certain folder. It can be shared instantly with a user or a group.

```
Usage: synophotos create [OPTIONS] NAME

  creates albums and folders

Options:
  -a, --album               creates an album
  -f, --folder              creates a folder
  -ff, --from-folder TEXT   id of folder to populate album with
  -p, --parent-id INTEGER   parent id of the folder
  -s, --share-with INTEGER  share album with
  --help                    Show this message and exit.
```

### `id`

Helper for finding ids.

```
Usage: synophotos id [OPTIONS] ELEMENT

  helps finding ids of various things

Options:
  -a, --album   search for album id
  -f, --folder  search for folder id
  -g, --group   search for group id
  -u, --user    search for user id
  --help        Show this message and exit.
```

### `list`

```
Usage: synophotos list [OPTIONS] [NAME]

  lists objects

Options:
  -a, --albums             lists albums
  -f, --folders            lists folders
  -g, --groups             lists groups
  -i, --items              lists items
  -p, --parent_id INTEGER  id of the parent (only valid when listing items or
                           folders)
  -r, --recursive          include all folders recursively
  -u, --users              lists users
  --help                   Show this message and exit.
```

### `profile`

```
Usage: synophotos profile [OPTIONS]

  shows the name of the currently active profile

Options:
  --help  Show this message and exit.
```

### `share-album`

Shares the album with the provided id. The permission, the user and the group to share with can be set via the
respective parameters.

```
Usage: synophotos share-album [OPTIONS] ALBUM_ID

  shares an album

Options:
  -r, --role TEXT        permission role, can be "view", "download" or
                         "upload"
  -p, --public           shares an album publicly
  -uid, --user-id TEXT   shares an album with a user with the provided id
  -gid, --group-id TEXT  shares an album with a group with the provided id
  --help                 Show this message and exit.
```

### `share-folder`

The name of the command is misleading, as folders cannot be shared in Photos. Instead, an album will be created
from the contents of a folder and shared with either a user, a group or publicly.

```
Usage: synophotos share-folder [OPTIONS] FOLDER_ID

  creates an album from a folder and shares it

Options:
  -n, --album-name TEXT  name of the album to be created
  -r, --role TEXT        permission role, can be "view", "download" or
                         "upload"
  -p, --public           shares an album publicly
  -uid, --user-id TEXT   shares an album with a user with the provided id
  -gid, --group-id TEXT  shares an album with a group with the provided id
  --help                 Show this message and exit.
```

### `unshare-album`

Revokes the share status from an album.

```
Usage: synophotos unshare-album [OPTIONS] ALBUM_ID

  unshares an album

Options:
  --help  Show this message and exit.
```
