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
* SoundCloud has stopped registering apps so the only way to get an API key is from the dev console 
  Navigate to soundcloud.com and check for any XHR request params to find a `client_id` that can be used
* Use `sc-dl --set-api-key <CLIENT_ID>` to set the API key

## Usage
![usage](https://i.imgur.com/Vm8Hirx.gif)
#### Options

    usage: soundcloud_dl.py [-h] [-t | -n | -u [URL]] [--set-api-key SET_API_KEY]
                            [-s] [-d DIR] [-a] [-l] [-e EXCLUDE [EXCLUDE ...]]
                            [-i INCLUDE [INCLUDE ...]] [--limit LIMIT]
                            [-r RANGE RANGE] [-g [GENRE]]

    optional arguments:
      -h, --help            show this help message and exit
      -t, --top             Downloads the top 10 tracks across all genres
      -n, --new             Downloads 10 new tracks across all genres
      -u [URL], --url [URL]
                            URL to download tracks from
      --set-api-key SET_API_KEY
                            sets the soundcloud API key
      -s, --similar         Downloads 10 tracks similar to the track in the URL
      -d DIR, --dir DIR     Directory to save tracks in. Defaults to current
                            working directory
      -a, --all             Download all tracks (Uploads and likes)
      -l, --likes           Download only liked tracks.
      -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                            Enter track numbers to exclude.
      -i INCLUDE [INCLUDE ...], --include INCLUDE [INCLUDE ...]
                            Enter track numbers to include
      --limit LIMIT         Maximum number of tracks to download
      -r RANGE RANGE, --range RANGE RANGE
                            Enter range of tracks to download.
      -g [GENRE], --genre [GENRE]
                            use with --top to get top tracks from a specific genre


* sc-dl can be used instead of soundcloud-dl
* `--top`, `--new` and `--url` arguments are mutually exclusive
* The url can be a link to a user, a track or a user's playlists. Downloads a user's uploads unless --all or --likes options are given
* Adding the --include option overrides the --exclude option
* Example : `sc-dl https://soundcloud.com/aaasrith --dir D:\Music`
* Example : `sc-dl https://soundcloud.com/aaasrith --dir D:\Music --exclude 1 2 3`
* Example : `sc-dl https://soundcloud.com/aaasrith/closurewithaclause -s`

### Contributions
If you want to add features, improve them, or report issues, feel free to send a pull request!
