# soundcloud-dl
[![Downloads](https://pepy.tech/badge/soundcloud-dl)](https://pepy.tech/project/soundcloud-dl)

A small command-line program to download tracks from soundcloud.com
You'll need to get an API key since there are rate limits on streams

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

#### Options
     soundcloud_dl.py [-h] [-t] [-n] [-s] [-d DIR] [-a] [-l]
                           [-e EXCLUDE [EXCLUDE ...]] [-i INCLUDE [INCLUDE ...]]
                           [--limit LIMIT] [-r RANGE RANGE] [-g [GENRE]]
                           [url]

     positional arguments:
       url                   URL to download tracks from

     optional arguments:
       -h, --help            show this help message and exit
       -t, --top             Downloads the top 10 tracks across all genres
       -n, --new             Downloads 10 new tracks across all genres
       -s, --similar         Downloads 10 tracks similar to the track in the URL
       -d DIR, --dir DIR     Directory to save tracks in. Default value is the
                             current working directory
       -a, --all             Download all tracks (Uploads and likes)
       -l, --likes           Download only liked tracks.
       -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                             Enter track numbers to exclude.
       -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                             Enter track numbers to include
       --limit LIMIT         Maximum number of tracks to download
       -r RANGE RANGE, --range RANGE RANGE
                             Enter range of tracks to download
       -g [GENRE], --genre [GENRE]
                             use with --top to get top tracks from a specific genre
                             
* sc-dl can be used instead of soundcloud-dl
* `--top`, `--new` and `URL` arguments are mutually exclusive
* The url can be a link to a user, a track or a user's playlists. Downloads a user's uploads unless --all or --likes options are given
* Adding the --include option overrides the --exclude option
* Example : `sc-dl https://soundcloud.com/aaasrith --dir D:\Music`
* Example : `sc-dl https://soundcloud.com/aaasrith --dir D:\Music --exclude 1 2 3`
* Example : `sc-dl https://soundcloud.com/aaasrith/closurewithaclause -s`

### Contributions
If you want to add features, improve them, or report issues, feel free to send a pull request!
