
# Synophotos CLI - Getting Started

## Installation and Configuration

The CLI is currently not yet available on pip. For this reason the only way for an installation is via git clone + pip:

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

## Commands

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
>> synophotos root
3
```

This simply fetches the root folder and returns its id, in this case `3`. We can now use the id to see if the root folder
has children:

```bash
>> synophotos list 3

  id   │ filename      │ filesize │ folder_id │ owner_user_id
╶──────┼───────────────┼──────────┼───────────┼───────────────╴
  1817 │ 'image_1.jpg' │ 1122567  │ 3         │ 2
  1797 │ 'image_2.jpg' │ 1031072  │ 3         │ 2
  1822 │ 'image_3.jpg' │ 824677   │ 3         │ 2
```

This lists the photos contained in the folder with the id `3`. The photos itself also have ids, which are shown in the
first column of the table. The same works with listing existing folders:

```bash
>> synophotos list -f

  id  │ name            │ parent │ owner_user_id │ shared
╶─────┼─────────────────┼────────┼───────────────┼────────╴
  35  │ '/Holiday'      │ 3      │ 2             │ False
  4   │ '/Birthday      │ 3      │ 2             │ False
```

Or with albums ... you get the idea ...:

```bash
>> synophotos list -a

  id │ name          │ item_count │ owner_user_id │ shared
╶────┼───────────────┼────────────┼───────────────┼────────╴
  2  │ 'My Birthday' │ 31         │ 2             │ True
  1  │ 'Private'     │ 10         │ 2             │ False
```
