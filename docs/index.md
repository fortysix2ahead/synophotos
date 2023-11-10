
# Synophotos CLI - Getting Started

## Installation and Configuration

It's recommended to install synophotos into a virtual environment. So we need to create one first:

Use pip to create and activate a virtual environment:

```bash
mkdir synophotos; pip -m venv synophotos; source synophotos/bin/activate
```

Now install synophotos into the newly create venv:

```bash
pip install synophotos
```

This will create executable scripts within the `synophotos/bin` folder. For now, only `synophotos` is supported
(other scripts might come later).

Next thing to do is to create two configuration files, `config.yaml` and `profiles.yaml`. Both are located in
`$USER_CONFIGURATION_FOLDER/synophotos/`. USER_CONFIGURATION_FOLDER is located in `~/.config` in Linux,
in `~/Library/Application Support/` in Mac OS X and in `~\AppData\Roaming\` in Windows.

You can create the configuration files with sample content by running:

```bash
synophotos init
```

`profiles.yaml` contains the URLs and credentials of (multiple) Synology stations:

```yaml
user_one:
  url: "https://my.synology.photos.server.example.com"
  account: "user1"
  password: "password1"

user_two:
  url: "https://my.synology.photos.server.example.com"
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
  -d, --debug    outputs debug information (implies --verbose)
  -v, --verbose  outputs verbose log information
  --help         Show this message and exit.

Commands:
  albums   lists existing albums and their ids
  count    counts items
  create   creates albums
  folders  lists existing folders and their ids
  groups   lists existing groups and their ids
  id       helps finding ids of various things
  init     initializes the application
  items    lists items
  profile  shows the name of the currently active profile
  root     gets the id of the root folder
  share    shares an album
  unshare  unshares an album
  users    lists existing users and their ids
  version  prints version information
```

## Identifiers (ids)

For now, most commands are working based on ids. What's an id? Each album, photo, user etc. in Synology Photos
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
>> synophotos items -f 3

  id   │ filename      │ filesize │ folder_id │ owner_user_id
╶──────┼───────────────┼──────────┼───────────┼───────────────╴
  1817 │ 'image_1.jpg' │ 1122567  │ 3         │ 2
  1797 │ 'image_2.jpg' │ 1031072  │ 3         │ 2
  1822 │ 'image_3.jpg' │ 824677   │ 3         │ 2
```

This lists the photos contained in the folder with the id `3`. The photos itself also have ids, which are shown in the
first column of the table. The same works with listing existing folders:

```bash
>> synophotos folders

  id  │ name            │ parent │ owner_user_id │ shared
╶─────┼─────────────────┼────────┼───────────────┼────────╴
  35  │ '/Holiday'      │ 3      │ 2             │ False
  4   │ '/Birthday      │ 3      │ 2             │ False
```

Or with albums ... you get the idea ...:

```bash
>> synophotos albums

  id │ name          │ item_count │ owner_user_id │ shared
╶────┼───────────────┼────────────┼───────────────┼────────╴
  2  │ 'My Birthday' │ 31         │ 2             │ True
  1  │ 'Private'     │ 10         │ 2             │ False
```
