import json, requests
from config import browser_id, client_id
from requests.adapters import HTTPAdapter

class SoundCloudClient(object):
    def __init__(self, args=None):
        self.API_V1 = "https://api.soundcloud.com"
        self.API_V2 = "https://api-v2.soundcloud.com"
        self.browser_id = browser_id
        self.session = requests.Session()
        self.session.mount("http://", adapter = HTTPAdapter(max_retries = 3))
        self.session.mount("https://", adapter = HTTPAdapter(max_retries = 3))

    def get_uploaded_tracks(self, user_id, limit=9999):
        url_params = {
            "client_id": browser_id,
            "limit": limit ,
            "offset": 0
        }
        url = "{}/users/{}/tracks".format(self.API_V2, user_id)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = json_payload["collection"]
        return tracks

    def get_liked_tracks(self, user_id, no_of_tracks=10):
        url_params = {
            "client_id": client_id,
            "limit": no_of_tracks,
            "offset": 0
        }
        url = "{}/users/{}/likes".format(self.API_V2, user_id)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = filter(lambda x: 'playlist' not in x, json_payload["collection"])
        return list(map(lambda x: x['track'], tracks))

    def get_recommended_tracks(self, track, no_of_tracks=10):
        url_params = {
            "client_id": browser_id,
            "limit": no_of_tracks,
            "offset": 0
        }
        recommended_tracks_url = "{}/tracks/{}/related".format(self.API_V2, track.id)
        r = self.session.get(recommended_tracks_url, params=url_params)
        tracks = json.loads(r.text)["collection"]
        tracks = map(lambda x: x["track"], tracks[:no_of_tracks])
        return list(tracks)

    def get_charted_tracks(self, kind, genre, limit=9999):
        url_params = {
            "limit": limit,
            "genre": "soundcloud:genres:" + genre,
            "kind": kind,
            "client_id": browser_id
        }
        url = "{}/charts".format(self.API_V2)
        response = self.session.get(url, params=url_params)
        json_payload = json.loads(response.text)
        tracks = json_payload["collection"]
        return tracks
