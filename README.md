# soundcloud-dl
A small command-line program to download tracks from soundcloud.com 

==================================================================
##Installation

####From Source
* Clone the repo or download the zip
* Make sure you have pip installed
* `cd` to the folder
* `pip -install -r "requirements.txt"`

##Usage
* On the terminal or Command Prompt Type
  `python soundcloud-dl.py "url" "directory"`
* The url can be a link to a user, a track or a user's playlists
* Example : `python soundcloud-dl.py "https://soundcloud.com/stringofasymptotes" "D:\Music"`
  
###Dependencies
* soundcloud - To work with the soundcloud API
* Requests - for retrieving HTML
* Mutagen - To tag mp3 files and add album art
