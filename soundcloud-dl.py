from downloader import downloader
import sys,os

if __name__ == '__main__':
	downloader = downloader.Downloader()
	downloader.url = sys.argv[1]
	try:
		downloader.dirname = sys.argv[2]
	except IndexError:
		downloader.dirname = os.getcwd()
	downloader.Download()