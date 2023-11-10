
# Getting Started

## Installation

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

## Configuration

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

## Next Steps

Now that synophotos is configured, you can check if everything works by asking for the id
of your root folder. This command should return a number if everything is ok.

```bash
>> synophotos root
3
```

Read more about available commands in [usage](usage.md) and [command reference](cli.md).
