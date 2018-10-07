import soundcloud, requests, os, re, sys
import socket, json
from soundcloud import resource
from .utils import download_file
from .config import secret
from requests.adapters import HTTPAdapter
from halo import Halo 

class SoundcloudDownloader(object):
	def __init__(self, args=None):
		self.args = args
		self.url = args.url
		self.dirname = args.dir
		self.client = soundcloud.Client(client_id=secret)
		self.API_V1 = "https://api.soundcloud.com"
		self.API_V2 = "https://api-v2.soundcloud.com"
		self.download_count = 0
		self.session = requests.Session()
		self.session.mount('http://', adapter = HTTPAdapter(max_retries = 3))
		self.session.mount('https://', adapter = HTTPAdapter(max_retries = 3))

	def getFilename(self, metadata):
		return self.validateName("{}-{}.{}".format(metadata['artist'], metadata['title'], metadata['format']))

	def getTrackUrl(self, track):
		if track['downloadable']: 
			return track['download_url']
		if track['streamable']: 
			if 'stream_url' in track:
				return track['stream_url']
			for transcoding in track['media']['transcodings']:
				if transcoding['format']['protocol'] == 'progressive':
					r = self.session.get(transcoding['url'], params={'client_id': secret})
					return json.loads(r.text)['url']  

	def getTrackMetadata(self, track):
		artist = 'unknown'
		if 'publisher_metadata' in track and track['publisher_metadata']:
			artist = track['publisher_metadata'].get('artist', '')
		elif 'user' in track or not artist:
			artist = track['user']['username']
		return {
			'title': str(track.get('title', track['id'])),
			'artist': artist,
			'year': str(track.get('release_year', '')),
			'genre': str(track.get('genre', '')),
			'format': track.get('original_format', 'mp3')		
		}

	def getSingleTrack(self, track):
		if isinstance(track, resource.Resource): track = track.fields()
		metadata = self.getTrackMetadata(track)
		filename = self.getFilename(metadata)
		url = self.getTrackUrl(track)
		download_file(filename, url, params={'client_id': secret})
		self.download_count += 1

	def getMultipleTracks(self, tracks):
		for _, track in filter(lambda x: self.checkTrackNumber(x[0]), enumerate(tracks)):
			self.getSingleTrack(track)

	def getPlaylist(self, playlist):
		print("{} tracks found in playlist".format(len(playlist.tracks)))
		self.getMultipleTracks(playlist.tracks)
	
	def checkTrackNumber(self, index):
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

	def getUploadedTracks(self, user):
		spinner = Halo(text='Fetching uploads')
		spinner.start()			
		tracks = self.client.get('/tracks', id=user.id)
		spinner.stop()
		print('Found {} uploads'.format(len(tracks)))
		self.getMultipleTracks(tracks)          

	def getRecommendedTracks(self, track, no_of_tracks=10):
		recommended_tracks_url = '{}/tracks/{}/related'.format(self.API_V2, track.id)
		params = {
			'client_id': secret,
			'limit': no_of_tracks,
			'offset': 0
		}
		r = self.session.get(recommended_tracks_url, params=params)
		tracks = json.loads(r.text)['collection']
		self.getMultipleTracks(tracks)

	def getLikedTracks(self):
		spinner = Halo(text='Fetching liked tracks')
		spinner.start()		
		liked_tracks = self.client.get('/resolve', url=self.url + '/likes')
		spinner.stop()
		print('{} liked track(s) found'.format(len(liked_tracks)))
		self.getMultipleTracks(liked_tracks)

	def validateName(self, name):
		return re.sub('[\\/:*"?<>|]', '_', name)

	def getChartedTracks(self, kind, no_of_tracks=10):
		url_params = {
			'limit': no_of_tracks,
			'genre': 'soundcloud:genres:' + self.args.genre,
			'kind': kind,
			'client_id': secret
		}
		url = '{}/charts'.format(self.API_V2)
		tracks = []
		spinner = Halo(text='Fetching {} {} tracks'.format(no_of_tracks, kind))
		spinner.start()
		while len(tracks) < no_of_tracks:
			response = self.session.get(url, params=url_params)
			json_payload = json.loads(response.text)
			tracks += json_payload['collection']
			url = json_payload['next_href']
		spinner.stop()
		tracks = map(tracks[:no_of_tracks], lambda x: x['track'])
		self.getMultipleTracks(tracks)

	def main(self):
		os.chdir(self.dirname)
		if self.args.top:
			self.getChartedTracks('top')
		if self.args.new:
			self.getChartedTracks('trending')
		spinner = Halo(text='Resolving URL')
		spinner.start()		
		data = self.client.get('/resolve', url=self.url) if self.url else None
		spinner.stop()
		if isinstance(data, resource.Resource):
			if data.kind == 'user':
				print("User profile found")
				folder = self.validateName(data.username)
				if not os.path.isdir(folder): os.mkdir(folder)
				os.chdir(os.path.join(os.getcwd(), folder))
				print("Saving in: " + os.getcwd())
				if self.args.all or self.args.likes:
					self.getLikedTracks()
				if not self.args.likes:
					self.getUploadedTracks(data)
			elif data.kind == 'track':
					print("Single track found")
					print("Saving in: " + os.getcwd())
					if self.args.similar:
						self.getRecommendedTracks(data)
					self.getSingleTrack(data)
			elif data.kind == 'playlist':
				print("Single playlist found.")
				folder = self.validateName(data.user['username'])
				if not os.path.isdir(folder):
					os.mkdir(folder)
				os.chdir(os.path.join(os.getcwd(), str(folder)))
				self.getPlaylist(data)
		elif isinstance(data, resource.ResourceList):
			if data[0].kind == 'playlist':
				print("%d playlists found" % (len(data)))
				for playlist in playlists:
					self.getPlaylist(playlist)
			elif data[0].kind == 'track':
				self.getMultipleTracks(data)
