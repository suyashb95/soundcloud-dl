import soundcloud, requests, os, re, sys
import socket, json

from tqdm import tqdm
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC
from mutagen.id3 import ID3, TIT2, TPE1, TCON, TDRC, APIC
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from halo import Halo

def set_api_key(key):
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
    api_key_config = "client_id='{}'".format(key)
    with open(config_file_path, 'w') as config_file:
        config_file.write(api_key_config)
    print("API key set successfully")

def validate_name(name):
        return re.sub('[\\/:*"?<>|]', "_", name)
        
def get_filename(metadata):
    return validate_name("{}-{}.{}".format(metadata["artist"], metadata["title"], metadata["format"]))

def does_file_exist(filename, actual_size=None):
    return os.path.isfile(filename) and (not actual_size or os.path.getsize(filename) >= float(actual_size))

def download_file(session, filename, url, params={}, silent=False):
    if not silent:
        spinner = Halo(text='Connecting to stream...')
        spinner.start()
    response = session.get(url, stream=True, params=params)
    if not silent: spinner.stop()
    file_size = float(response.headers['content-length']) if 'content-length' in response.headers else 0
    if does_file_exist(filename, file_size):
        if not silent: print("{} already exists, skipping\n".format(filename))
        return filename
    if not silent: print("Saving as: {}".format(filename))
    if not silent: print("File Size: {0:.2f}".format(file_size/(1000**2)))
    with open(filename, 'wb') as file:
        for chunk in tqdm(response.iter_content(chunk_size=1024), total=file_size/1024 + 1, unit='KB', unit_scale=True, disable=silent):
            if chunk: file.write(chunk)
    if not silent: print("Download complete\n")

def tag_file(filename, metadata):
    image = None
    if metadata['artwork_url']: download_file('artwork.jpg', metadata['artwork_url'], silent=True)
    if os.path.isfile('artwork.jpg'): image = open('artwork.jpg', 'rb').read()
    if filename.endswith('.mp3'):
        audio = MP3(filename, ID3=ID3)
        audio.add_tags()
        if image: audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image))
        audio.tags["TIT2"] = TIT2(encoding=3, text=metadata['title'])
        audio.tags["TPE1"] = TPE1(encoding=3, text=metadata['artist'])
        audio.tags["TDRC"] = TDRC(encoding=3, text=metadata['year'])
        audio.tags["TCON"] = TCON(encoding=3, text= metadata['genre'])
        audio.save()
    elif filename.endswith('.flac'):
        audio = FLAC(filename)
        audio.add_tags()
        if image: audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=image))
        audio.tags['title'] = metadata['title']
        audio.tags['artist'] = metadata['artist']
        audio.tags['year'] = metadata['year']
        audio.tags['genre'] = metadata['genre']
        audio.save()
    elif filename.endswith('.m4a'):
        audio = MP4(filename)
        audio.add_tags()
        covr = []
        if image: covr.append(MP4Cover(image, MP4Cover.FORMAT_JPEG))
        audio.tags['covr'] = covr
        audio.tags['title'] = metadata['title']
        audio.tags['artist'] = metadata['artist']
        audio.tags['year'] = metadata['year']
        audio.tags['genre'] = metadata['genre']
        audio.save()
    if os.path.isfile('artwork.jpg'): os.remove('artwork.jpg')