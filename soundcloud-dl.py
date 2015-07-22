from downloader import downloader
import sys,argparse,os

parser = argparse.ArgumentParser()
parser.add_argument('--url',default = None, type = str, help = 'URL to download tracks from.')
parser.add_argument('--dir',default = os.getcwd(), type = str, help = 'Directory to save tracks in. Default value is the current working directory.')
parser.add_argument('--all',default = False,action = 'store_true', help = 'Download all tracks.(Uploads and likes)')
parser.add_argument('--likes',default = False,action = 'store_true', help = 'Download only liked tracks.')

if __name__ == '__main__':
	args = parser.parse_args()
	if args.url == None:
		print "No URL entered."
		sys.exit(0)
	downloader = downloader.Downloader(args)
	try:
		downloader.Download()
	except KeyboardInterrupt:
		print "\nExiting."
		sys.exit(0)