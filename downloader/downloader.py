import soundcloud,json,requests

class Downloader():
	
	def __init__(self,url = None,dirname = None):
		self.url = url
		self.dirname = dirname
		self.client = soundcloud.Client(client_id = 'f21537b8df8ad884d6ac791d2f53868e')
		
	def getUserId(self):
		user = self.client.get('/resolve',url = self.url)
		return user.id
		
	def getTracks(self):
		user_id = self.getUserId()
		tracks = self.client.get('/tracks',user_id = user_id)
		for track in tracks:
			print track.title.encode('utf-8')
			
	def getLikes(self):
		url = 'https://api.soundcloud.com/users/' + str(self.getUserId()) + '/favorites?client_id=f21537b8df8ad884d6ac791d2f53868e'
		response = requests.get(url)
		liked_tracks = json.loads(response.text)
		for track in liked_tracks:
			print track['title'].encode('utf-8')
		