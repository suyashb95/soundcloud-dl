import soundcloud,json,requests,os,re,sys
from config import secret
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4,MP4Cover
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC,APIC
from soundcloud import resource

class Downloader():
	
	def __init__(self,url = None,dirname = None):
		self.url = url
		self.dirname = dirname
		self.client = soundcloud.Client(client_id = secret)
		
	def Resolver(self):
		try:
			data = self.client.get('/resolve',url = self.url)
		except:
			return None
		return data
		
	def getSingleTrack(self,track):
		metadata = {'title':track.title.encode('utf-8'),
					'artist':track.user['username'].encode('utf-8'),
					'year':track.release_year,
					'genre':track.genre.encode('utf-8'),
				}
		if(track.downloadable):
			filename = track.title.encode('utf-8')+'.'+track.original_format
			url = track.download_url + '?client_id='+secret
		else:
			filename = metadata['title']  + '.mp3'
			url = track.stream_url + '?client_id=' + secret
		new_filename = self.getFile(filename,url)
		self.tagFile(new_filename,metadata,track.artwork_url)
				
	def getUploadedTracks(self,user):
		tracks = self.client.get('/tracks',user_id = user.id)
		print str(len(tracks)) + " track(s) found."
		for track in tracks:
			self.getSingleTrack(track)
			
	def getLikedTracks(self,user):
		liked_tracks = client.get('/resolve',url = self.url + '/likes')
		print str(len(liked_tracks)) + " track(s) found."
		for track in liked_tracks:
			for track in tracks:
				self.getSingleTrack(track)
	
	def getPlaylist(self,playlists):
		for playlist in playlists:
			tracks = resource.ResourceList(playlist.tracks)
			print str(len(track)) + " track(s) found."
			for track in tracks:
					self.getSingleTrack(track)
		
	def progressBar(self,done,file_size):
		percentage = ((done/file_size)*100)
		sys.stdout.flush()
		sys.stdout.write('\r')	
		sys.stdout.write('[' + '#'*int((percentage/5)) + ' '*int((100-percentage)/5) + '] ')
		sys.stdout.write(' | %.2f' % percentage + ' %')
			
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
				return filename
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
		return filename
		print "\nDownload complete."
		
	def tagFile(self,filename,metadata,art_url):
		self.getFile('artwork.jpg',art_url,True)
		if(filename.endswith('.mp3')):
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
		elif(filename.endswith('.flac')):
			audio = FLAC(filename)
			try:
				audio.add_tags()
			except:
				pass
			audio.tags['title'] = metadata['title']
			audio.tags['artist'] = metadata['artist']
			audio.tags['year'] = metadata['year']
			audio.tags['genre'] = metadata['genre']
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
			audio.save()
		elif(filename.endswith('.m4a')):
			audio = MP4(filename)
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
			covr = []
			covr.append(MP4Cover(image, MP4Cover.FORMAT_JPEG))
			audio.tags['covr'] = covr
			audio.tags['title'] = metadata['title']
			audio.tags['artist'] = metadata['artist']
			#audio.tags['year'] = metadata['year']
			audio.tags['genre'] = metadata['genre']
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
		data = self.Resolver()
		if data is not None:
			try:
				if data.kind == 'user':
					folder = re.sub('[\/:*"?<>|]','_',data.username.encode('utf-8'))
					if not os.path.isdir(folder):
						os.mkdir(folder)
					os.chdir(os.getcwd() + '\\' + str(folder))
					print "Saving in : " + os.getcwd()
					self.getUploadedTracks(data)			
				elif data.kind == 'track':
					print "Saving in : " + os.getcwd()
					self.getSingleTrack(data)
			except AttributeError:
				if data[0].kind == 'playlist':
					folder = re.sub('[\/:*"?<>|]','_',data[0].user['username'].encode('utf-8'))
					if not os.path.isdir(folder):
						os.mkdir(folder)
					os.chdir(os.getcwd() + '\\' + str(folder))
					print "Saving in : " + os.getcwd()
					self.getPlaylist(data)
		else:
			print "Invalid URL"
			
			
		