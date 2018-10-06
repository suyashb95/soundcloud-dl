# soundcloud-dl
A small command-line program to download tracks from soundcloud.com
You'll need to acquire an API key since there are rate limits on streams

## Installation

#### Using Pip
* Run `pip install soundcloud_dl`

#### From Source
* Clone the repo or download the zip
* Make sure you have pip installed
* `cd` to the folder
* `pip install -r "requirements.txt"`

### Getting an API key
* Log in to Soundcloud and register a new app [here](http://soundcloud.com/you/apps). That should give you an API key
* Navigate to the folder where the package is installed `Python36\Lib\site-packages\soundcloud-dl\downloader`
* Create a file called `config.py` and add your API key there as shown in the file config-example.py

## Usage

* usage: soundcloud-dl.py [-h] [--top] [--new] [URL] [--dir DIR] [--all] [--likes] [--include] [--exclude] [--limit]
* sc-dl can be used instead of soundcloud-dl
* `--top`, `--new` and `URL` arguments are mutually exclusive
* The url can be a link to a user, a track or a user's playlists. Downloads a user's uploads unless --all or --likes options are given
* Adding the --include option overrides the --exclude option
* Example : `python soundcloud-dl.py https://soundcloud.com/stringofasymptotes --dir D:\Music`
* Example : `python soundcloud-dl.py https://soundcloud.com/stringofasymptotes --dir D:\Music --exclude 1 2 3`
* Example : `python soundcloud-dl.py https://soundcloud.com/stringofasymptotes/surrender-and-reality/recommended`

## Options
     -h, --help  show this help message and exit
     -t, --top   Downloads the top 10 tracks across all genres
     -n, --new   Downloads 10 new tracks across all genres     
     --dir DIR   Directory to save tracks in. Default value is the current
                 working directory.
     --all       Download all tracks. (Uploads and likes)
     --likes     Download only liked tracks.
     --exclude   Exclude a list of tracks. (List of space separeted integers)
     --include   Specifically download a list of tracks. (List of space separated integers)
     --limit     Limits the number of tracks to be downloaded. (Single integer)
     --range     Range of track numbers to download. (Two space separated integers)
  
### Dependencies
* soundcloud - To work with the soundcloud API
* requests - To retrieve HTML
* mutagen - To tag audio files and add album art

### Contributions
If you want to add features, improve them, or report issues, feel free to send a pull request!

### Contributors
- [Suyash458](https://github.com/Suyash458)
