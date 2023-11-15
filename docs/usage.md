
# Usage

## Commands

The general structure of a synophotos command is

```
synophotos [OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS]
```

The currently available commands and options are the following. To learn about all the details,
refer to the [command reference](cli.md). Currently, there are only three global options, which are
`--verbose`, which prints additional information, `--debug`, which implies `--verbose`and prints
debug information, and `--force`, which disables interactive mode and assumes `yes` for confirmations.

**A friendly warning**: don't use `--debug` unless you really need to, as it might
print **a lot of messages** (mainly HTTP requests and responses)! Using `--verbose` is usually enough
to learn what synophotos is doing behind the scenes.

```
Usage: synophotos [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --debug    outputs debug information (implies --verbose)
  -f, --force    forces the execution of commands and skips confirmation
                 dialogs
  -v, --verbose  outputs verbose log information
  --help         Show this message and exit.

Commands:
  albums    lists existing albums and their ids
  count     counts items
  create    creates albums
  download  download items
  folders   lists existing folders and their ids
  groups    lists existing groups and their ids
  id        helps finding ids of various things
  init      initializes the application
  items     lists items
  profile   shows the name of the currently active profile
  root      gets the id of the root folder
  share     shares an album
  show      displays information on items, folder and albums (this is...
  sync      sync
  unshare   unshares an album
  users     lists existing users and their ids
  version   prints version information
```

## Names and Identifiers

It's very important to understand Synology's identifiers (ids) as a core concept, that's why we'll discuss them here in the
very beginning. All commands of synophotos are working based on ids (at least internally). What's an id? Each album, photo,
user etc. in Synology Photos has a numeric identifier, which uniquely identifies this item. While names of those items **might**
be unique, it's not guaranteed that they are. For instance, you can have multiple albums named _Birthday_, perfectly existing 
along each other. Most commmands of synophotos also work based on names of items, but might fail, when a provided name refers
to more than one element. Keep this in mind!

As ids are of utmost importance there are two dedicated commands for identifying things. The simplest one is used for identifying
the root folder of your personal space (which is 3 in this example):

```bash
>> synophotos root
3
```

To find the ids of albums, folders, users and groups, use the `id` command. As an example, let's ask for the id of the album named
_Birthday_. The `id` command is not case-sensitive. But beware, it will silently return the id of the first matching element only!

```bash
>> synophotos id -a birthday
17
```

## Finding Things

Of course, you know what folders, photos and albums you have. But might not have all of them in your mind. That's why synophotos
offers several commands for finding and listing things.

### Folders

For finding folders, use the `folders` command:

```bash
>> synophotos folders

  id  │ name            │ parent │ owner_user_id │ shared
╶─────┼─────────────────┼────────┼───────────────┼────────╴
  35  │ '/Holiday'      │ 3      │ 2             │ False
  4   │ '/Birthday      │ 3      │ 2             │ False
```


This lists folders living in the root folder of your personal space. In order to restrict the display of folders to ones matching a certain name, use the name
as an argument:

```bash
>> synophotos folders birth

  id  │ name            │ parent │ owner_user_id │ shared
╶─────┼─────────────────┼────────┼───────────────┼────────╴
  4   │ '/Birthday      │ 3      │ 2             │ False
```

In order to list folders inside a parent folder, use the parent folder's id along with the `-p` switch:

```bash
>> synophotos folders -p 4

  id   │ name            │ parent │ owner_user_id │ shared
╶──-───┼─────────────────┼────────┼───────────────┼────────╴
  26   │ '/2022'         │ 4      │ 2             │ False
  27   │ '/2023'         │ 4      │ 2             │ False
```

Finally, you can also list all available folders recursively by using `-r` switch. However, depending on the amount of data you have, this might take a while.

### Albums

Finding albums works very similar to finding folders, with the exception that there are no parent albums, and therefore you cannot list albums recursively.
For finding albums, use the `albums` command.

```bash
>> synophotos albums

  id │ name          │ item_count │ owner_user_id │ shared
╶────┼───────────────┼────────────┼───────────────┼────────╴
  2  │ 'My Birthday' │ 31         │ 2             │ True
  1  │ 'Private'     │ 10         │ 2             │ False
```

### Photos

Finding photos is not very different from finding folders and albums. To display lists of photos use the `items` command. In order to use the command you have
to provide either a parent folder:

```bash
>> synophotos items -f 4

  id   │ filename      │ filesize │ folder_id │ owner_user_id
╶──────┼───────────────┼──────────┼───────────┼───────────────╴
  1817 │ 'image_1.jpg' │ 1122567  │ 4         │ 2
  1797 │ 'image_2.jpg' │ 1031072  │ 4         │ 2
  1822 │ 'image_3.jpg' │ 824677   │ 4         │ 2
```

... or a parent album:

```bash
>> synophotos items -a 2

  id   │ filename      │ filesize │ folder_id │ owner_user_id
╶──────┼───────────────┼──────────┼───────────┼───────────────╴
  1817 │ 'image_1.jpg' │ 1122567  │ 4         │ 2
  1797 │ 'image_2.jpg' │ 1031072  │ 4         │ 2
  1822 │ 'image_3.jpg' │ 824677   │ 4         │ 2
```

The `items` command also supports filtering for names and recursive listing, just like the `folders` command. **But beware**, using `--recursive` for listing photos
on a deep folder structure might take a very long time!

### Users and Groups

Apart from finding photos and the like, synophotos can also give you information about existing users and groups. This is important when it comes to sharing.
To display information about groups and users, use the commands `users`:

```bash
>> synophotos users
  id   │ name         │ type
╶──────┼──────────────┼────────╴
  1001 │ 'bethany'    │ 'user'
  1002 │ 'jay'        │ 'user'
  1003 │ 'bob'        │ 'user'
```

... and `groups`. Note that this will include Synology's groups related to Photos only, not all existing groups of the system:

```bash
>> synophotos users
 id     │ name             │ type
╶───────┼──────────────────┼─────────╴
  101   │ 'administrators' │ 'group'
  65536 │ 'family'         │ 'group'
  100   │ 'users'          │ 'group'
```

## Creating Albums

Synophotos allows creating and populating albums from existing content. The command for doing that is `create`. This will create an empty album and return the
is of the album.

```bash
>> synophotos create Holiday
35
```

It's also possible to populate the album from existing content. Provide a folder or a folder id and all photos of that folder will be added to the newly
created album:

```bash
>> synophotos create -f holidays Holiday
35
>> synophotos create -fid 14 Holiday
36
```

## Sharing Albums

Albums can be shared and unshared. For doing that the commands `share` and `unshare` exist. To share an album publicly use the `-p` switch. You must provide
either an album name or an id. In addition, you need to provide a role, which can be `view`, `download` or `upload`.

```bash
>> synophotos share -r view holiday
>> synophotos share -id 35 -p -r view
```

To share an album with certain user, provide the name of a user or its id:

```bash
>> synophotos share -r view -u bethany holiday
>> synophotos share -r view -uid 1001 holiday
```

This works with groups as well:

```bash
>> synophotos share -r view -g family holiday
>> synophotos share -r view -gid 65536 holiday
```

An album can be unshared later:

```bash
>> synophotos unshare holiday
```

## Downloading and Syncing

Synophotos allows to download single items, respectively sync albums to a local disk. This is still work in progress, as downloading items in original size
is still broken (unable to figure out the right call to the API, for details see https://github.com/fortysix2ahead/synophotos/issues/8

The `download` command is of little use as it only takes ids as arguments, but internally it's the basis for syncing. It has been exposed nevertheless.
The usage is:

```
Usage: synophotos download [OPTIONS] ID

Options:
  -d, --destination TEXT  destination folder for downloaded items  [required]
  -s, --size TEXT         download image in specified size, can be one of [sm,
                          m, xl, original]
  --help                  Show this message and exit.
```

By using the `sync` command it's possible to download a whole album to the local disk. The usage is:

```
Usage: synophotos sync [OPTIONS] ALBUMS...

  sync

Options:
  -d, --destination TEXT  destination folder to sync to  [required]
  --help                  Show this message and exit.
```

It takes one or more strings which are matched against all existing albums, including shared ones. All items from those albums will be downloaded to the
provided destination folder. **Important: any .jpg files in the destination folder which are not contained in the given albums will be removed!**

```
❯ synophotos sync -d ~/Temp holiday birthday
Sync will add 45 files, remove 17 files and skip 12 files, continue? [y/n]:
```

By default, there will be a confirmation before anything is done. This can be skipped by using the `--force` option. 

## Other Commands

There are some other commands, that might come handy from time to time.

### Init

You can create configuration file with sample content by using the `init` command.

### Profiles

To display the currently active profile, use the `profile` command:

```bash
>> synophotos profile
bethany
```

### Show

The `show` command can be used to examine items, folders or albums. This might not be very interesing for the normal user,
but can be used to check what information is returned from the server. 

```
Usage: synophotos show [OPTIONS] [ID]

Options:
  -a, --album-id   treat provided id as album id
  -f, --folder-id  treat provided id as folder id
  -i, --item-id    treat provided id as item id (this is the default)
  --help           Show this message and exit.
```

A sample output looks like this (getting details about an album):

```
❯ synophotos show -a 64
                           ╷
  attribute                │ value
╶──────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╴
  'cant_migrate_condition' │ None
  'condition'              │ {'general_tag': [261], 'general_tag_policy': 'and', 'item_type': [6, 4, 3, 2, 0], 'user_id': 5}
  'create_time'            │ 1699809584
  'end_time'               │ 1053393427
  'freeze_album'           │ False
  'id'                     │ 64
  'item_count'             │ 5
  'name'                   │ 'Holidays 2023'
  'owner_user_id'          │ 5
  'passphrase'             │ 'Abcdefghi'
  'shared'                 │ True
  'sort_by'                │ 'default'
  'sort_direction'         │ 'default'
  'start_time'             │ 1053280888
  'temporary_shared'       │ False
  'type'                   │ 'condition'
  'version'                │ 385506
  'additional'             │ Additional(
                           │     access_permission=None,
                           │     description=None,
                           │     exif={},
                           │     flex_section=[5],
                           │     orientation=None,
                           │     orientation_original=None,
                           │     person=<class 'list'>,
                           │     provider_count=1,
                           │     provider_user_id=None,
                           │     rating=None,
                           │     resolution={},
                           │     sharing_info={
                           │         'enable_password': False,
                           │         'expiration': 0,
                           │         'is_expired': False,
                           │         'mtime': 1699959538,
                           │         'owner': {'id': 5, 'name': 'klaus'},
                           │         'passphrase': 'Abcdefghi',
                           │         'permission': [
                           │             {'db_id': 2, 'id': 1000, 'name': 'user0', 'role': 'view', 'type': 'user'},
                           │             {'db_id': 12, 'id': 1001, 'name': 'user1', 'role': 'download', 'type': 'user'}
                           │         ],
                           │         'privacy_type': 'private',
                           │         'sharing_link': 'https://example.com/mo/sharing/Abcdefghi',
                           │         'type': 'album'
                           │     },
                           │     tag=[],
                           │     thumbnail={'cache_key': '26435_1695192057', 'm': 'ready', 'preview': 'broken', 'sm': 'ready', 'unit_id': 26435, 'xl': 'ready'}
                           │ )
                           ╵
  ```

## Hidden Commands

Some commands are hidden from the user interface as they are either not finished or are not intended to be used by the end user. Currently, these commands are:

- `payload`: For displaying the payload that is sent to the server. This is for development only!
- `search`: For searching things on the server. In general this already works, but the results are not display in a nice way.
