
# Usage

## Commands

The general structure of a synophotos command is

```
synophotos [OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS]
```

The currently available commands and options are the following. To learn about all the details,
refer to the [command reference](cli.md). Currently, there are only two global options, which are
`--verbose`, which prints additional information, and `--debug`, which implies `--verbose`and prints
debug information. **A friendly warning**: don't use `--debug` unless you really need to as it might
print **a lot of messages**! Using `--verbose` is usually enough to learn what synophotos is doing behind
the scenes.

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
