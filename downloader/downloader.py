import soundcloud, requests, os, re, sys
import socket, json
from soundcloud import resource
from .utils import download_file, tag_file, validate_name, get_filename
from .context import client_id
from requests.adapters import HTTPAdapter
from halo import Halo

class SoundcloudDownloader(object):
    def __init__(self, args=None):
        self.args = args
        self.url = args.url
        self.dirname = args.dir
        self.client = soundcloud.Client(client_id=client_id)
        self.API_V2 = "https://api-v2.soundcloud.com"
        self.API_V1 = "https://api.soundcloud.com"
        self.download_count = 0
        self.session = requests.Session()
        self.session.mount("http://", adapter = HTTPAdapter(max_retries = 3))
        self.session.mount("https://", adapter = HTTPAdapter(max_retries = 3))

    def can_download_track(self, track):
        is_downloadable = track["downloadable"] and "download_url" in track
        is_streamable = track["streamable"]
        has_stream_url = "stream_url" in track
        for transcoding in track["media"]["transcodings"]:
            if transcoding["format"]["protocol"] == "progressive":
                has_stream_url = True
                break
        return is_downloadable or (is_streamable and has_stream_url)

    def get_track_url(self, track):
        if track["downloadable"] and "download_url" in track:
            return ("{}?client_id={}".format(track["download_url"], client_id), track.get("original_format", "mp3"))
        if track["streamable"]:
            if "stream_url" in track:
                return ("{}?client_id={}".format(track["stream_url"], client_id), "mp3")
            for transcoding in track["media"]["transcodings"]:
                if transcoding["format"]["protocol"] == "progressive":
                    r = self.session.get(transcoding["url"], params={"client_id": client_id})
                    return (json.loads(r.text)["url"] , "mp3")
        return (None, None)

    def get_track_metadata(self, track):
        artist = "unknown"
        if "publisher_metadata" in track and track["publisher_metadata"]:
            artist = track["publisher_metadata"].get("artist", "")
        elif "user" in track or not artist:
            artist = track["user"]["username"]
        url, fileFormat = self.get_track_url(track)
        return {
            "title": str(track.get("title", track["id"])),
            "artist": artist,
            "year": str(track.get("release_year", "")),
            "genre": str(track.get("genre", "")),
            "format": fileFormat,
            "download_url": url,
            "artwork_url": track["artwork_url"]
        }

    def get_single_track(self, track):
        if isinstance(track, resource.Resource): track = track.fields()
        metadata = self.get_track_metadata(track)
        filename = get_filename(metadata)
        if metadata['download_url']:
            download_file(self.session, filename, metadata["download_url"])
            try:
                tag_file(filename, metadata)
            except:
                if os.path.isfile("artwork.jpg"): os.remove("artwork.jpg")
            self.download_count += 1
        else:
            print('Cannot download {}'.format(metadata['title']))

    def get_multiple_tracks(self, tracks):
        for _, track in filter(lambda x: self.check_track_number(x[0]), enumerate(tracks)):
            self.get_single_track(track)

    def get_playlist(self, playlist):
        print("{} tracks found in playlist".format(len(playlist.tracks)))
        self.get_multiple_tracks(playlist.tracks)

    def check_track_number(self, index):
        if self.download_count == self.args.limit:
            return False
        if self.args.include and index + 1 in self.args.include:
            return True
        if self.args.exclude and index + 1 in self.args.exclude:
            return False
        if self.args.range:
            if not self.args.range[0] <= index + 1 <= self.args.range[1]:
                return False
        return True

    def get_recommended_tracks(self, track, no_of_tracks=10):
        params = {
            "client_id": client_id,
            "limit": no_of_tracks,
            "offset": 0
        }
        spinner = Halo(text="Fetching tracks similar to {}".format(track.title))
        spinner.start()
        recommended_tracks_url = "{}/tracks/{}/related".format(self.API_V2, track.id)
        r = self.session.get(recommended_tracks_url, params=params)
        spinner.stop()
        tracks = r.json()["collection"]
        print("Found {} similar tracks".format(len(tracks)))
        self.get_multiple_tracks(tracks)

    def get_charted_tracks(self, kind, no_of_tracks=10):
        url_params = {
            "limit": no_of_tracks,
            "genre": "soundcloud:genres:" + self.args.genre,
            "kind": kind,
            "client_id": client_id
        }
        url = "{}/charts".format(self.API_V2)
        tracks = []
        spinner = Halo(text="Fetching {} {} tracks".format(no_of_tracks, kind))
        spinner.start()
        while len(tracks) < no_of_tracks:
            json_payload = self.session.get(url, params=url_params).json()
            tracks += json_payload["collection"]
            tracks = list(filter(lambda track: self.can_download_track(track['track']), tracks))			
            url = json_payload["next_href"]
        spinner.stop()
        tracks = map(lambda x: x["track"], tracks[:no_of_tracks])
        self.get_multiple_tracks(tracks)

    def get_uploaded_tracks(self, user):
        no_of_tracks = self.args.limit if self.args.limit else 9999
        params = {
            "client_id": client_id,
            "limit": no_of_tracks,
            "offset": 0
        }
        tracks = []
        spinner = Halo(text="Fetching uploads")
        spinner.start()
        url = "{}/users/{}/tracks".format(self.API_V2, user.id)
        while url:
            json_payload = self.session.get(url, params=params).json()
            tracks += json_payload["collection"]
            tracks = list(filter(lambda track: self.can_download_track(track), tracks))
            if len(tracks) >= no_of_tracks: break
            url = json_payload.get("next_href", None)
        spinner.stop()
        print("Found {} uploads".format(len(tracks)))
        self.get_multiple_tracks(tracks)

    def get_liked_tracks(self, user):
        no_of_tracks = self.args.limit if self.args.limit else 9999
        params = {
            "client_id": client_id,
            "limit": no_of_tracks,
            "offset": 0
        }
        tracks = []
        spinner = Halo(text="Fetching uploads")
        spinner.start()
        url = "{}/users/{}/likes".format(self.API_V2, user.id)
        while url:
            json_payload = self.session.get(url, params=params).json()
            tracks += list(filter(lambda x: 'playlist' not in x, json_payload["collection"]))
            tracks = list(filter(lambda track: self.can_download_track(track['track']), tracks))			
            if len(tracks) >= no_of_tracks: break
            url = json_payload.get("next_href", None)
        spinner.stop()
        tracks = [track['track'] for track in tracks]
        print("Found {} likes".format(len(tracks)))
        self.get_multiple_tracks(tracks)

    def main(self):
        os.chdir(self.dirname)
        if self.args.top:
            self.get_charted_tracks("top")
            return 
        if self.args.new:
            self.get_charted_tracks("trending")
            return
        spinner = Halo(text="Resolving URL")
        spinner.start()
        params = {
            "url": self.url,
            "client_id": client_id
        }
        url = "{}/resolve".format(self.API_V2)
        res = self.session.get(url, params=params)
        if not res.ok:
            print("Could not get a valid response from the SoundCloud API. Please check the API key")
            return
        res = res.json()
        data = resource.Resource(res)
        spinner.stop()
        if isinstance(data, resource.Resource):
            if data.kind == "user":
                print("User profile found")
                folder = validate_name(data.username)
                if not os.path.isdir(folder): os.mkdir(folder)
                os.chdir(os.path.join(os.getcwd(), folder))
                print("Saving in: " + os.getcwd())
                if self.args.all or self.args.likes:
                    self.get_liked_tracks(data)
                if not self.args.likes:
                    self.get_uploaded_tracks(data)
            elif data.kind == "track":
                    print("Single track found")
                    print("Saving in: " + os.getcwd())
                    if self.args.similar:
                        self.get_recommended_tracks(data)
                    self.get_single_track(data)
            elif data.kind == "playlist":
                print("Single playlist found.")
                folder = validate_name(data.user["username"])
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                os.chdir(os.path.join(os.getcwd(), str(folder)))
                self.get_playlist(data)
        elif isinstance(data, resource.ResourceList):
            if data[0].kind == "playlist":
                print("%d playlists found" % (len(data)))
                for playlist in data:
                    self.get_playlist(playlist)
            elif data[0].kind == "track":
                self.get_multiple_tracks(data)
