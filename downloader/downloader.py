import soundcloud, requests, os, re, sys
from config import secret, browser_id
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TCON, TDRC, APIC
from soundcloud import resource
from time import sleep
from contextlib import closing
import socket, json

class soundcloudDownloader(object):

    def __init__(self, args=None):
        self.args = args
        self.url = args.url
        self.dirname = args.dir
        self.client = soundcloud.Client(client_id=secret)
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
        self.completed = 0

    def Resolver(self, action, data, resolve=False):
        try:
            if resolve:
                data = self.client.get(str(action), url=str(data))
            else:
                data = self.client.get(str(action), user_id=data)
        except (requests.exceptions.ConnectionError,
                TypeError,
                socket.error):
            print "Connection error. Retrying in 15 seconds."
            sleep(15)
            self.Resolver(action, data, resolve)
        except requests.exceptions.HTTPError:
            print "Invalid URL."
            sys.exit(0)
        except KeyboardInterrupt:
            print "Exiting."
            sys.exit(0)
        if data is not None:
            return data

    def connectionHandler(self, url, stream=False, timeout=15):
        try:
            response = self.session.get(url, stream=stream, timeout=timeout)
            assert response.status_code == 200
            return response
        except (requests.exceptions.ConnectionError,
                TypeError,
                socket.error):
            print "Connection error. Retrying in 15 seconds."
            sleep(15)
            self.connectionHandler(url, stream)
        except (AssertionError,
                requests.exceptions.HTTPError):
            print "Connection error or invalid URL."
            return
        except KeyboardInterrupt:
            print "Exiting."
            sys.exit(0)

    def getSingleTrack(self, track):
        if isinstance(track, resource.Resource):
            track = track.fields()
        metadata = {
            'title':track['title'].encode('utf-8'),
            'artist':track['user']['username'].encode('utf-8'),
            'year':track.get('release_year', ''),
            'genre':track['genre'].encode('utf-8')
        }
        try:
            if track['downloadable']:
                filename = (track['user']['username'] + ' - ' + \
                track['title'] + '.' + track['original_format']).encode('utf-8')
                url = track['download_url'] + '?client_id='+secret
            else:
                filename = (track['user']['username'] + ' - ' + \
                track['title'] + '.mp3').encode('utf-8')
                url = track['stream_url'].split('?')[0] + '?client_id='+secret
        except AttributeError:
            filename = (track['user']['username'] + ' - ' +  \
            track['title'] + '.mp3').encode('utf-8')
            url = 'https://api.soundcloud.com/tracks/' + \
            str(track['id']) + '/stream?client_id=' + secret
        try:
            new_filename = self.getFile(filename, url)
            self.completed += 1
            self.tagFile(new_filename, metadata, track['artwork_url'])
        except KeyboardInterrupt:
            sys.exit(0)

    def getPlaylists(self, playlists):
        if isinstance(playlists, resource.ResourceList):
            for playlist in playlists:
                for track in playlist.tracks:
                    self.getSingleTrack(track)
        else:
            print "%d tracks found in this playlist" % (len(playlists.tracks))
            for track in playlists.tracks:
                self.getSingleTrack(track)
    
    def checkTrackNumber(self,index):
        if self.args.limit is not None:
            if self.completed == self.args.limit:
                return
        if self.args.include is not None:
            if index + 1 not in self.args.include:
                if not self.args.range:
                    return False
        if self.args.exclude is not None:
            if index + 1 in self.args.exclude:
                print "Skipping " + str(track.title.encode('utf-8'))
                return False
        if self.args.range is not None:
            if not self.args.range[0] <= index + 1 <= self.args.range[1]:
                if self.args.include:
                    if index + 1 not in self.args.include:
                        return False
                else:
                    return False
        return True

    def getUploadedTracks(self, user):
        tracks = self.Resolver('/tracks', user.id)
        for index, track in enumerate(tracks):
            if self.checkTrackNumber(index):
                self.getSingleTrack(track)				

    def getRecommendedTracks(self, track, no_tracks):
        recommended_tracks_url = "https://api-v2.soundcloud.com/tracks/"
        recommended_tracks_url += str(track.id) + "/related?client_id="
        recommended_tracks_url += str(browser_id) + "&limit="
        recommended_tracks_url += str(no_tracks) + "&offset=0"
        recommended_tracks = self.session.get(recommended_tracks_url)
        recommended_tracks = json.loads(recommended_tracks.text)['collection']
        for track in recommended_tracks:
            self.getSingleTrack(track)

    def getLikedTracks(self):
        liked_tracks = self.Resolver('/resolve', self.url + '/likes', True)
        print str(len(liked_tracks)) + " liked track(s) found."
        for index, track in enumerate(liked_tracks):
            if self.checkTrackNumber(index):
                self.getSingleTrack(track)

    def progressBar(self, done, file_size):
        percentage = ((done/file_size)*100)
        sys.stdout.flush()
        sys.stdout.write('\r')
        sys.stdout.write('[' + '#'*int((percentage/5)) + ' '*int((100-percentage)/5) + '] ')
        sys.stdout.write(' | %.2f' % percentage + ' %')

    def validateName(self, name):
        return  re.sub('[\\/:*"?<>|]', '_', name)

    def getFile(self, filename, link, silent=False):
        new_filename = self.validateName(filename)
        if link is not None:
            if silent:
                try:
                    with closing(self.connectionHandler(link, True, 15)) as response:
                        with open(new_filename, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    file.write(chunk)
                                    file.flush()
                    return new_filename
                except (socket.error,
                        requests.exceptions.ConnectionError):
                    self.getFile(filename, link, silent)
                except KeyboardInterrupt:
                    print "\nExiting."
                    sys.exit(0)
            print "\nConnecting to stream..."
            with closing(self.connectionHandler(link, True, 5)) as response:
                print "Response: "+ str(response.status_code)
                file_size = float(response.headers['content-length'])
                if os.path.isfile(new_filename):
                    if os.path.getsize(new_filename) >= long(file_size):
                        print new_filename + " already exists, skipping."
                        return new_filename
                    else:
                        os.remove(new_filename)
                        print "Incomplete download, restarting."
                print "File Size: " + '%.2f' % (file_size/(1000**2)) + ' MB'
                print "Saving as: " + new_filename
                done = 0
                try:
                    with open(new_filename, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                                file.flush()
                                done += len(chunk)
                                self.progressBar(done, file_size)
                    if os.path.getsize(new_filename) < long(file_size):
                        os.remove(new_filename)
                        print "\nConnection error. Restarting in 15 seconds."
                        sleep(15)
                        self.getFile(filename, link, silent)
                    print "\nDownload complete."
                    return new_filename
                except (socket.error,
                        requests.exceptions.ConnectionError):
                    os.remove(new_filename)
                    self.getFile(filename, link, silent)
                except KeyboardInterrupt:
                    print "\nExiting."
                    os.remove(new_filename)
                    raise KeyboardInterrupt
        else:
            return new_filename

    def tagFile(self, filename, metadata, art_url):
        image = None
        if art_url is not None:
            self.getFile('artwork.jpg', art_url, True)
            try:
                with open('artwork.jpg', 'rb') as file:
                    image = file.read()
            except:
                pass
        if filename.endswith('.mp3'):
            audio = MP3(filename, ID3=ID3)
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
            try:
                audio.tags["TPE1"] = TPE1(encoding=3, text=metadata['artist'].encode('utf-8'))
            except:
                pass
            audio.tags["TDRC"] = TDRC(encoding=3, text=unicode(metadata['year']))
            audio.tags["TCON"] = TCON(encoding=3, text=metadata['genre'])
            audio.save()
        elif filename.endswith('.flac'):
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
        elif filename.endswith('.m4a'):
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
        data = self.Resolver('/resolve', self.url, True)
        if data is not None:
            if isinstance(data, resource.Resource):
                if data.kind == 'user':
                    print "User profile found."
                    folder = self.validateName(data.username.encode('utf-8'))
                    if not os.path.isdir(folder):
                        os.mkdir(folder)
                    os.chdir(os.getcwd() + '\\' + str(folder))
                    print "Saving in : " + os.getcwd()
                    if self.args.all:
                        self.getUploadedTracks(data)
                        self.getLikedTracks()
                    elif self.args.likes:
                        self.getLikedTracks()
                    else:
                        self.getUploadedTracks(data)
                elif data.kind == 'track':
                    if 'recommended'  in self.url: 
                        no_tracks = self.args.limit if self.args.limit else 5
                        print "Downloading " + str(no_tracks) + " related tracks"
                        self.getRecommendedTracks(data, no_tracks)
                    else:
                        print "Single track found."
                        print "Saving in : " + os.getcwd()
                        self.getSingleTrack(data)
                elif data.kind == 'playlist':
                    print "Single playlist found."
                    folder = self.validateName(data.user['username'].encode('utf-8'))
                    if not os.path.isdir(folder):
                        os.mkdir(folder)
                    os.chdir(os.getcwd() + '\\' + str(folder))
                    self.getPlaylists(data)
            elif isinstance(data, resource.ResourceList):
                if self.url.endswith('likes'):
                    user_url = self.url[:-6]
                    user = self.Resolver('/resolve', user_url, True)
                    folder = self.validateName(user.username.encode('utf-8'))
                else:
                    folder = self.validateName(data[0].user['username'].encode('utf-8'))
                if not os.path.isdir(folder):
                    os.mkdir(folder)
                os.chdir(os.getcwd() + '\\' + str(folder))
                print "Saving in : " + os.getcwd()
                if data[0].kind == 'playlist':
                    print "%d playlists found." % (len(data))
                    self.getPlaylists(data)
                elif data[0].kind == 'track':
                     self.getUploadedTracks(data)

        else:
            print "Network error or Invalid URL."
            sys.exit(0)