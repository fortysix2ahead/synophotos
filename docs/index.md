
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

Next thing to do is to create a configuration file, `config.yaml`. It's located in
`$USER_CONFIGURATION_FOLDER/synophotos/`. USER_CONFIGURATION_FOLDER is located in `~/.config` in Linux,
in `~/Library/Application Support/` in Mac OS X and in `~\AppData\Roaming\` in Windows.

You can create the configuration file with sample content by running:

```bash
synophotos init
```

Note that you need to edit `config.yaml` right afterward as subsequent commands will fail when synophotos
tries to connect to a non-existing sample server.

`config.yaml` simply contains URLs and credentials of (multiple) Synology stations as profiles
and the currently active profile which is used when commands are executed in a terminal:

```yaml
profile: "user_one"
profiles:
    user_one:
      url: "https://my.synology.photos.server.example.com"
      account: "user1"
      password: "password1"
    
    user_two:
      url: "https://my.synology.photos.server.example.com"
      account: "user2"
      password: "password2"
```

## Next Steps

Now that synophotos is configured, you can check if everything works by asking for the id
of your root folder. This command should return a number if everything is ok.

```bash
>> synophotos root
3
```

Read more about available commands in [usage](usage.md) and [command reference](cli.md).
