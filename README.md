# fastdown
Interim site scraper.

## Requirements
  - [Python 2.7]
  - [pip]
  - [fastdown]

[Python 2.7]: https://www.python.org/downloads/
[pip]: https://pip.pypa.io/en/latest/installing.html
[fastdown]: https://github.com/metaist/fastdown/archive/master.zip

## Setup
Once you've got these things installed, unzip fastdown and run the following
in the unzipped directory:

```bash
./install.sh
```

## Configuration
The configuration is stored in `config.json`. Here is a sample configuration
file:

```JSON
{
  "proxies": {
    "http": "http://proxy.example.com",
    "https": "https://proxy.example.com"
  },
  "sites": {
    "weeklystandard.com": {
      "encrypt": true,
      "folder": ".",
      "password": "password",
      "username": "email@example.com"
    }
  }
}
```

  - `<None|dict> proxies` - protocols mapped to their proxy urls, or `None`
    if there is a direct connection to the internet
  - `<dict> sites` - sites mapped to their configurations
    - `<bool> encrypt` - if `True`, this section will be encrypted when using
      `--encrypt` (see below).
    - `<str> username` - account user name
    - `<str> password` - account password
    - `<str> folder` - path of where to save downloaded files

## Usage
```bash
./fastdown.sh [-c CONFIG] [-s SITE] [-p PASSWORD] [--encrypt | --decrypt]
```
  - `-c`, `--config` - path to config file (default: `config.json`)
  - `-s`, `--site` - name of site to process
    (currently only `weeklystandard.com`)
  - `-p`, `--password` - password for encrypted configuration file
  - `-e`, `--encrypt` - encrypt the configuration file before exiting
  - `-d`, `--decrypt` - decrypt the configuration file before exiting

## License
Licensed under the [MIT License].

[MIT License]: https://github.com/metaist/fastdown/blob/master/LICENSE
