
# Synophotos CLI

Synophotos Command Line Interface (CLI) is an attempt to enable remote control of certain functions in Synology Photos from a terminal.

## Installation and Configuration

The CLI is currently not yet available. For this reason the only way for an installation is via git clone + pip:

```bash
git clone https://github.com/fortysix2ahead/synophotos
cd synophotos
pip -m venv venv
source ./venv/bin/activate
pip install -e .
```

This will create executable scripts within the `venv\bin` folder. For now, only `synophotos` is supported
(other commands might come later).

Next thing to do is to create two configuration files, `config.yaml` and `profiles.yaml`. Both are located in
`$USER_CONFIGURATION_FOLDER/synophotos/`. USER_CONFIGURATION_FOLDER is located in `~/.config` in Linux,
in `~/Library/Application Support/` in Mac OS X and in `~\AppData\Roaming\` in Windows.

`profiles.yaml` contains the URLs and credentials of (multiple) Synology stations:
```yaml
user_one:
  url: "https://my.synology.nas.com"
  account: "user1"
  password: "password1"

user_two:
  url: "https://my.synology.nas.com"
  account: "user2"
  password: "password2"
```

`config.yaml` simply contains the currently active profile which is used when commands are executed in a terminal:
```yaml
profile: "user_one"
```

## Usage

The currently available commands and options are:

```
Usage: synophotos [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --debug  Print debug information
  --help       Show this message and exit.

Commands:
  count    counts various things
  create   creates albums and folders
  id       helps finding ids of various things
  list     lists objects
  profile  shows the name of the currently active profile
  root     gets the id of the root folder
  search   search for various things
  share    shares an album or folder
  unshare  unshares an album
```

## Identifiers (ids)

For now, all commands are working based on ids. What's an id? Each album, photo, user etc. in Synology Photos
has a unique id. Synology uses numbers for working with things, so it's essential to know which item has which
id number.

The most simple command is

```bash
synophotos root
3
```

This simply fetches the root folder and returns its id, in this case `3`. We can now use the id to see if the root folder
has children:

```bash
synophotos list 3
  id   │ filename      │ filesize │ folder_id │ owner_user_id
╶──────┼───────────────┼──────────┼───────────┼───────────────╴
  1817 │ 'image_1.jpg' │ 1122567  │ 3         │ 2
  1797 │ 'image_2.jpg' │ 1031072  │ 3         │ 2
  1822 │ 'image_3.jpg' │ 824677   │ 3         │ 2
```

This lists the photos contained in the folder with the id `3`. The photos itself also have ids, which are shown in the
first column of the table. The same works with listing existing folders:

```bash
synophotos list-folders
  id  │ name            │ parent │ owner_user_id │ shared
╶─────┼─────────────────┼────────┼───────────────┼────────╴
  35  │ '/Holiday'      │ 3      │ 2             │ False
  4   │ '/Birthday      │ 3      │ 2             │ False
```

Or with albums ... you get the idea ...:

```bash
synophotos list-albums
  id │ name          │ item_count │ owner_user_id │ shared
╶────┼───────────────┼────────────┼───────────────┼────────╴
  2  │ 'My Birthday' │ 31         │ 2             │ True
  1  │ 'Private'     │ 10         │ 2             │ False
```

## Command Reference

Important: don't rely on the command names and parameters yet. They will likely change in the future and are not
considered stable yet! Also read this section first to find out what commands are there and how they need to be used.

### `count-albums`

```
Usage: synophotos count-albums [OPTIONS]

  counts the number of albums

Options:
  --help  Show this message and exit.
```

### `count-folders`

```
Usage: synophotos count-folders [OPTIONS] [PARENT_ID]

  counts the number of folders

Options:
  --help  Show this message and exit.
  ```

### `count-items`

Counts the number of items in either an album or a folder.

```
Usage: synophotos count-items [OPTIONS]

  counts the number of items

Options:
  -f, --folder-id TEXT  id of the parent folder
  -a, --album-id TEXT   id of the parent album
  --help                Show this message and exit.
```

### `create-album`

Creates an album with the provided name. By default, the album is empty, but can be populated with images from
a certain folder. It can be shared instantly with a user or a group.

```
Usage: synophotos create-album [OPTIONS] NAME

  creates a new album

Options:
  -f, --from-folder TEXT  id of folder to populate album with
  -s, --share-with TEXT   share album with
  --help                  Show this message and exit.
```

### `get-root-folder`

Returns the id of the root folder.

```
Usage: synophotos get-root-folder [OPTIONS]

  gets the root folder

Options:
  --help  Show this message and exit.
```

### `id`

Helper for finding ids. Currently only user and groups are supported.

```
Usage: synophotos id [OPTIONS] ELEMENT

  helps finding ids of various things

Options:
  -u, --user   search for user id
  -g, --group  search for group id
  --help       Show this message and exit.
```

### `list-albums`

Lists all albums along with their sharing status.

```
Usage: synophotos list-albums [OPTIONS]

  lists albums

Options:
  --help  Show this message and exit.
```

### `list-folders`

Lists folders which are children of the folder with the provided id. It can search recursively when the flag `-r`
is provided. In addition, it can restrict itself to folders with a certain string in its name (`-n` flag).

```
Usage: synophotos list-folders [OPTIONS] [PARENT_ID]

  lists folders

Options:
  -r, --recursive  include all folders recursively
  -n, --name TEXT  folders only which name contains provided name (case
                   insensitive)
  --help           Show this message and exit.
```

### `list-items`

Lists items inside a folder or album. By default, the output will be paged, which can be turned off by using the
flag `-a`. The flag `-r` list items recursively. **Beware that this might be a long-running operation!**

```
Usage: synophotos list-items [OPTIONS] [PARENT_ID]

  lists items

Options:
  -a, --all        skip paging and list all items
  -r, --recursive  includes all items recursively
  --help           Show this message and exit.
```

### `list-user-groups`

```
Usage: synophotos list-user-groups [OPTIONS]

  lists users and groups

Options:
  --help  Show this message and exit.
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
