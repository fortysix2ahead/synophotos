
# Synophotos - Synology Photos Command Line Interface

[![Documentation Status](https://readthedocs.org/projects/synophotos/badge/?version=latest)](https://synophotos.readthedocs.io/en/latest/?badge=latest)

Synophotos Command Line Interface (CLI) is an attempt to enable remote control of certain functions in Synology Photos from a terminal.

## Features

- connect to a Synology Photos instance and run various commands remotely 
- list and count albums, folders and images
- list users and groups
- create albums and populate albums from existing items
- share and unshare albums

## Quickstart

Use pip to create and activate a virtual environment and install synophotos:

```bash
> mkdir synophotos
> pip -m venv synophotos
> source synophotos/bin/activate
> pip install synophotos
```

Initialize the application:

```bash
> synophotos init
A sample configuration file has been created in "$USER_CONFIG/synophotos/"
```

Edit the file `config.yaml` found in `$USER_CONFIG/synophotos/` and insert your server URL and credentials.

Run synophotos to check what albums you have:

```bash
> synophotos albums

  id │ name          │ item_count │ owner_user_id │ shared
╶────┼───────────────┼────────────┼───────────────┼────────╴
  2  │ 'My Birthday' │ 31         │ 2             │ True
  1  │ 'Private'     │ 10         │ 2             │ False
```

## Installation, Getting Started and Command Reference

The complete documentation is hosted at readthedocs.io: [http://synophotos.readthedocs.io/](http://synophotos.readthedocs.io/).

## Related Projects

- Synology API Wrapper (https://github.com/N4S4/synology-api)
- Unofficial Synology Photos API Documentation (https://github.com/zeichensatz/SynologyPhotosAPI)
