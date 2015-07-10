import soundcloud,json,requests,os,re,sys
from config import secret
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4,MP4Cover
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC,APIC
from soundcloud import resource
from time import sleep
from contextlib import closing

class Downloader():
	
	def __init__(self,args = None):
		self.args = args
		self.url = args.url
		self.dirname = args.dir
		self.client = soundcloud.Client(client_id = secret)
		self.session = requests.Session()
		self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
		self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
		
	def Resolver(self,action,data,resolve = False):
		try:
			if resolve:
				data = self.client.get(str(action),url = str(data))
			else:
				data = self.client.get(str(action),user_id = data)
		except requests.exceptions.ConnectionError:
			print "Connection error. Retrying in 15 seconds."
			sleep(15)
			return self.Resolver(action,data,resolve)
		except TypeError:
			print "Type error. Retrying in 15 seconds."
			sleep(15)
			return self.Resolver(action,data,resolve)
		except requests.exceptions.HTTPError:
			print "Invalid URL."
			return
		except KeyboardInterrupt:
			print "\nExiting."
			sys.exit(0)
		if data is not None:
			return data
	
	def connectionHandler(self,url,stream = False,timeout = 15):
		try:
			response = self.session.get(url,stream = stream,timeout = timeout)
			assert response.status_code == 200
			return response
		except requests.exceptions.ConnectionError:
			print "Network error.Retrying in 15 seconds."
			sleep(15)
			return self.connectionHandler(url,stream)
		except TypeError:
			print "Network error.Retrying in 15 seconds."
			sleep(15)
			return self.connectionHandler(url,stream)
		except AssertionError:
			print "Connection error or invalid URL."
			sys.exit(0) 
		except requests.exceptions.HTTPError:
			print "Invalid URL."
			return
		except KeyboardInterrupt:
			print "\nExiting."
			sys.exit(0)
				
	def getSingleTrack(self,track):
		if not isinstance(track,resource.Resource):
			track = resource.Resource(track)
		metadata = {'title':track.title.encode('utf-8'),
					'artist':track.user['username'].encode('utf-8'),
					'year':track.release_year,
					'genre':track.genre.encode('utf-8'),
				}
		if(track.downloadable):
			filename = (track.user['username'] + ' - ' + track.title + '.' + track.original_format).encode('utf-8')
			url = track.download_url + '?client_id='+secret
		else:
			filename = (track.user['username'] + ' - ' + track.title + '.mp3' ).encode('utf-8')
			url = track.stream_url + '?client_id=' + secret
		new_filename = self.getFile(filename,url)
		return new_filename
		self.tagFile(new_filename,metadata,track.artwork_url)
				
	def getPlaylists(self,playlists):
		if isinstance(playlists,resource.ResourceList):
			for playlist in playlists:
				for track in playlist.tracks:
					self.getSingleTrack(track)
		else:
			print "%d tracks found in this playlist" % (len(playlist.tracks))
			for track in playlists:
				self.getSingleTrack(track)
			
	def getUploadedTracks(self,user):
		tracks = self.Resolver('/tracks',user.id)
			#tracks = self.client.get('/tracks',user_id = user.id)
		for track in tracks:
			self.getSingleTrack(track)
			
	def getLikedTracks(self,user):
		liked_tracks = self.Resolver('/resolve',self.url + '/likes',True)
		print str(len(liked_tracks)) + " liked track(s) found."
		for track in liked_tracks:
			self.getSingleTrack(track)
		
	def progressBar(self,done,file_size):
		percentage = ((done/file_size)*100)
		sys.stdout.flush()
		sys.stdout.write('\r')	
		sys.stdout.write('[' + '#'*int((percentage/5)) + ' '*int((100-percentage)/5) + '] ')
		sys.stdout.write(' | %.2f' % percentage + ' %')
			
	def getFile(self,filename,link,silent = False):
		if link is not None:
			if silent:
				try:
					with closing(self.connectionHandler(link,True,5)) as response:
						with open(filename,'wb') as file:
							for chunk in response.iter_content(chunk_size=1024):
								if chunk:
									file.write(chunk)
									file.flush()
					return filename
				except:
					self.getFile(filename,link,True)			
			print "\nConnecting to stream..."
			try:
				with closing(self.connectionHandler(link,True,5)) as response:
					print "Response: "+ str(response.status_code)		
					file_size = float(response.headers['content-length'])	
					if(os.path.isfile(filename)):
						if os.path.getsize(filename) >= long(file_size):
							print filename + " already exists, skipping."
							return filename
						else:
							print "Incomplete download, restarting."
					print "File Size: " + '%.2f' % (file_size/(1000**2)) + ' MB'
					print "Saving as: " + filename
					done = 0
					try:
						with open(filename,'wb') as file:
							for chunk in response.iter_content(chunk_size=1024):
								if chunk:
									file.write(chunk)
									file.flush()
									done += len(chunk)
									self.progressBar(done,file_size)
									
						if os.path.getsize(filename) < long(file_size):
							print "\nConnection error. Restarting in 15 seconds."
							sleep(15)
							return self.getFile(filename,link,silent)
						print "\nDownload complete."
						return filename
					except KeyboardInterrupt:
						print "\nExiting."
						sys.exit(0)
			except KeyboardInterrupt:
				print "\nExiting." 
				sys.exit(0)
		else:
			return 

		
	def tagFile(self,filename,metadata,art_url):
		image = None
		if art_url is not None:
			self.getFile('artwork.jpg',art_url,True)
			try:
				with open('artwork.jpg','rb') as file:
					image = file.read()
			except:
				pass
		if(filename.endswith('.mp3')):
			audio = MP3(filename,ID3=ID3)
			try:
				audio.add_tags()
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
			audio.tags["TDRC"] = TDRC(encoding=3, text=unicode(metadata['year']))
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
			covr = []
			covr.append(MP4Cover(image, MP4Cover.FORMAT_JPEG))
			audio.tags['covr'] = covr
			audio.tags['title'] = metadata['title']
			audio.tags['artist'] = metadata['artist']
			#audio.tags['year'] = metadata['year']
			audio.tags['genre'] = metadata['genre']
			audio.save()
		if os.path.isfile('artwork.jpg'):	
			os.remove('artwork.jpg')
		
	def Download(self):
		if self.url is None:
			print "No URL entered."
			return
		elif 'soundcloud' not in self.url:
			print "Invalid URL"
			return
		try:
			if os.path.isdir(self.dirname):
				os.chdir(str(self.dirname))
			else:
				print "Directory doesn't exist."
				return
			print "Connecting ... "		
		except WindowsError:
			print "Invalid Directory"
			return
		data = self.Resolver('/resolve',self.url,True)
		if data is not None:
			if isinstance(data,resource.Resource):
				if data.kind == 'user':
					print "User profile found."
					folder = re.sub('[\/:*"?<>|]','_',data.username.encode('utf-8'))
					if not os.path.isdir(folder):
						os.mkdir(folder)
					os.chdir(os.getcwd() + '\\' + str(folder))
					print "Saving in : " + os.getcwd()
					if self.args.all:
						self.getUploadedTracks(data)
						self.getLikedTracks(data)
					elif self.args.likes:
						self.getLikedTracks(data)
					else:
						self.getUploadedTracks(data)			
				elif data.kind == 'track':
					print "Single track found."
					print "Saving in : " + os.getcwd()
					self.getSingleTrack(data)
				elif data.kind == 'playlist':
					print "Single playlist found."
					folder = re.sub('[\/:*"?<>|]','_',data.user['username'].encode('utf-8'))
					if not os.path.isdir(folder):
						os.mkdir(folder)
					os.chdir(os.getcwd() + '\\' + str(folder))
					self.getPlaylists(data)					
			elif isinstance(data,resource.ResourceList):
				if self.url.endswith('likes'):
					user_url = self.url[:-6]
					user = self.Resolver('/resolve',user_url,True)
					folder = re.sub('[\/:*"?<>|]','_',user.username.encode('utf-8'))
				else:
					folder = re.sub('[\/:*"?<>|]','_',data[0].user['username'].encode('utf-8'))
				if not os.path.isdir(folder):
					os.mkdir(folder)
				os.chdir(os.getcwd() + '\\' + str(folder))
				print "Saving in : " + os.getcwd()
				if data[0].kind == 'playlist':
					print "%d playlists found." % (len(data))		
					self.getPlaylists(data)
				elif data[0].kind == 'track':
					for track in data:
						self.getSingleTrack(track)
		else:
			print "Network error or Invalid URL"
			
			
		