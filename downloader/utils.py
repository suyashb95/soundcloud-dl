import soundcloud, requests, os, re, sys
import socket, json

from clint.textui import progress
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TCON, TDRC, APIC
from .config import secret
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

retries = 3
backoff_factor = 0.3
status_forcelist=(500, 502, 504)
session = requests.Session()
retry = Retry(total = retries, read = retries, connect = retries, backoff_factor = backoff_factor, status_forcelist = status_forcelist)
session.mount('http://', adapter = HTTPAdapter(max_retries = retry))
session.mount('https://', adapter = HTTPAdapter(max_retries = retry))

def does_file_exist(filename, actual_size):
	if os.path.isfile(filename):
		if os.path.getsize(filename) >= float(actual_size):
			return True
	return False

def download_file(filename, url, params, silent=False):
	if not silent: print("Connecting to stream...")
	response = session.get(url, stream=True, params=params)
	if not silent: print("Response: {}".format(str(response.status_code)))
	file_size = float(response.headers['content-length'])
	if does_file_exist(filename, file_size):
		if not silent: print("{} already exists, skipping".format(filename))
		return filename
	if not silent: print("File Size: {} MB".format(file_size/(1000**2)))
	if not silent: print("Saving as:{}".format(filename))
	with open(filename, 'wb') as file:
		for chunk in progress.bar(response.iter_content(chunk_size=1024), expected_size=file_size/1024 + 1):
			if chunk: file.write(chunk)
	if not silent: print("Download complete")

def tagFile(self, filename, metadata, art_url):
	if not file_done:
		return
	image = None
	if art_url is not None:
		download_file('artwork.jpg', art_url, True)
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
		if image:
			audio.tags.add(
				APIC(
					encoding=3,
					mime='image/jpeg',
					type=3,
					desc=u'Cover',
					data=image
				)
			)
		audio.tags["TIT2"] = TIT2(encoding=3, text=(metadata.get('title', '')))
		try:
			audio.tags["TPE1"] = TPE1(encoding=3, text=metadata.get('artist', ''))
		except:
			pass
		audio.tags["TDRC"] = TDRC(encoding=3, text=(metadata.get('year', '')))
		audio.tags["TCON"] = TCON(encoding=3, text=(metadata.get('genre', ' ')))
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