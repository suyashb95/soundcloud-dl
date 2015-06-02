import soundcloud,json,requests,os,HTMLParser,re,sys
from config import secret
class Downloader():
	
	def __init__(self,url = None,dirname = None):
		self.url = url
		self.dirname = dirname
		self.client = soundcloud.Client(client_id = secret)
		
	def getUser(self):
		user = self.client.get('/resolve',url = self.url)
		return user
		
	def getTracks(self):
		user_id = self.getUser().id
		tracks = self.client.get('/tracks',user_id = user_id)
		print str(len(tracks)) + " track(s) found."
		for track in tracks:
			metadata = {'title':track.title.encode('utf-8'),
						'artist':track.user['username'].encode('utf-8'),
						'year':track.release_year,
						'genre':track.genre.encode('utf-8'),
					}
			#self.getArtWork(track.artwork_url)
			if(track.downloadable):
				self.getFile(track.title.encode('utf-8'),track.stream_url + '?client_id='+seret)
			else:
				self.getFile(track.title.encode('utf-8'),track.download_url +  + '?client_id='+secret)
			
	def getLikedTracks(self):
		url = 'https://api.soundcloud.com/users/' + str(self.getUser().id) + '/favorites?client_id='+secret
		response = requests.get(url)
		liked_tracks = json.loads(response.text)
		print str(len(liked_tracks)) + " track(s) found."
		for track in liked_tracks:
			for track in tracks:
				metadata = {'title':track['title'],
							'artist':track['user']['username'].encode('utf-8'),
							'year':track['release_year'],
							'genre':track['genre'].encode('utf-8'),
							}
			#self.getArtWork(track.artwork_url)
				if(track.downloadable):
					self.getFile(track.title,track.stream_url)
				else:
					self.getFile(track.title,track.download_url)
		
	def progressBar(self,done,file_size):
		percentage = ((done/file_size)*100)
		sys.stdout.flush()
		sys.stdout.write('\r')	
		sys.stdout.write('[' + '#'*int((percentage/5)) + ' '*int((100-percentage)/5) + '] ')
		sys.stdout.write('%.2f' % percentage + ' %')
			
	def getFile(self,filename,link):
		print "Connecting to stream..."
		response = requests.get(str(link), stream=True)
		print "Response: "+ str(response.status_code)		
		file_size = float(response.headers['content-length'])
		filename = re.sub('[\/:*"?<>|]','_',filename) + '.mp3'
		if(os.path.isfile(filename)):
			if os.path.getsize(filename) >= long(file_size):
				print "File already exists, skipping."
				return
			else:
				print "Incomplete download, restarting."
		print "File Size: " + '%.2f' % (file_size/(1000**2)) + ' MB'
		print "Saving as: " + filename
		done = 0
		with open(filename,'wb') as file:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					file.write(chunk)
					file.flush()
					done += len(chunk)
					self.progressBar(done,file_size)
		print "\nDownload complete."
		#self.tagFile(filename,metadata)
		
	def tagFile(self,filename,metadata):
		audio = MP3(filename,ID3=ID3)
		try:
			audio.add_tags()
		except:
			pass
		with open('album-art.jpg','rb') as file:
			image = file.read()
		audio.tags.add(
			APIC(
				encoding=3,
				mime='image/jpeg',
				type=3,
				desc=u'Cover',
				data=image
				)
			)
		audio.tags["TIT2"] = TIT2(encoding=3, text=metadata['title'])
		audio.tags["TPE1"] = TPE1(encoding=3, text=metadata['artist'])
		audio.tags["TDRC"] = TDRC(encoding=3, text=unicode(metadata['year']))
		audio.tags[""]
		audio.save()

	def Download(self):
		if self.url is None:
			print "No URL entered."
			return
		elif 'soundcloud' not in self.url:
			print "Invalid URL"
			return
		try:
			if self.dirname is not None:
				os.chdir(str(self.dirname))
			print "Connecting ... "		
		except WindowsError:
			print "Invalid Directory"
			return
		parser = HTMLParser.HTMLParser()
		user = self.getUser()
		folder = re.sub('[\/:*"?<>|]','_',user.username.encode('utf-8'))
		if not os.path.isdir(folder):
			os.mkdir(folder)
		os.chdir(os.getcwd() + '\\' + str(folder))
		print "Saving in : " + os.getcwd()
		self.getTracks()
		