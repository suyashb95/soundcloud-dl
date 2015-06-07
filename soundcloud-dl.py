from downloader import downloader
import sys

if __name__ == '__main__':
	downloader = downloader.Downloader()
	downloader.url = sys.argv[1]
	downloader.dirname = sys.argv[2]
	downloader.Download()