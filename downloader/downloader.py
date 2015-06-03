import soundcloud,json,requests,os,HTMLParser,re,sys
from config import secret
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC,APIC

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
			if(track.downloadable):
				#filename = track.title.encode('utf-8')+'.'+track.original_format
				#url = track.download_url + '?client_id='+secret
				filename = track.title.encode('utf-8') + '.mp3'
				url = track.stream_url + '?client_id=' + secret
			else:
				filename = track.title.encode('utf-8') + '.mp3'
				url = track.stream_url + '?client_id=' + secret
			new_filename,tagged = self.getFile(filename,url)
			if not tagged:
				self.getFile('artwork.jpg',track.artwork_url,True)
				self.tagFile(new_filename,metadata)
			
	def getLikedTracks(self):
		url = 'https://api.soundcloud.com/users/' + str(self.getUser().id) + '/favorites?client_id='+secret
		response = requests.get(url)
		liked_tracks = json.loads(response.text)
		print str(len(liked_tracks)) + " track(s) found."
		for track in liked_tracks:
			for track in tracks:
				metadata = {'title':track['title'].encode('utf-8'),
							'artist':track['user']['username'].encode('utf-8'),
							'year':track['release_year'].encode('utf-8'),
							'genre':track['genre'].encode('utf-8'),
							}
				if(track.downloadable):
					filename = track.title.encode('utf-8')+'.'+track.original_format
					url = track.download_url + '?client_id='+secret
				else:
					filename = track.title.encode('utf-8') + '.mp3'
					url = track.stream_url +  + '?client_id='+secret
				new_filename,finished = self.getFile(filename,url)
				self.tagFile(new_filename,metadata)
		
	def progressBar(self,done,file_size):
		percentage = ((done/file_size)*100)
		sys.stdout.flush()
		sys.stdout.write('\r')	
		sys.stdout.write('[' + '#'*int((percentage/5)) + ' '*int((100-percentage)/5) + '] ')
		sys.stdout.write('%.2f' % percentage + ' %')
			
	def getFile(self,filename,link,silent = False):
		if silent and link is not None:
			response = requests.get(str(link), stream=True)
			with open(filename,'wb') as file:
				for chunk in response.iter_content(chunk_size=1024):
					if chunk:
						file.write(chunk)
						file.flush()
			return 
			
		print "\nConnecting to stream..."
		response = requests.get(str(link), stream=True)
		print "Response: "+ str(response.status_code)		
		file_size = float(response.headers['content-length'])
		filename = re.sub('[\/:*"?<>|]','_',filename)
		if(os.path.isfile(filename)):
			if os.path.getsize(filename) >= long(file_size):
				print filename + " already exists, skipping."
				return filename,True
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
		return filename,False
		print "\nDownload complete."
		
	def tagFile(self,filename,metadata):
		audio = MP3(filename,ID3=ID3)
		try:
			audio.add_tags()
		except:
			pass
		image = None
		try:
			with open('artwork.jpg','rb') as file:
				image = file.read()
		except:
			pass
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
		audio.tags["TDRC"] = TDRC(encoding=3, text=metadata['year'])
		audio.tags["TCON"] = TCON(encoding=3, text=metadata['genre'])
		audio.save()
		os.remove('artwork.jpg')

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
		