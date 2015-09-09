from downloader import downloader
import sys, argparse, os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default=None, type=str,
                        help='URL to download tracks from.')
    parser.add_argument('--dir', default=os.getcwd(), type=str,
                        help='''Directory to save tracks in.
                        Default value is the current working directory.''')
    parser.add_argument('--all', default=False, action='store_true',
                        help='Download all tracks.(Uploads and likes)')
    parser.add_argument('--likes', default=False, action='store_true',
                        help='Download only liked tracks.')
    parser.add_argument('--exclude', nargs='+', type=int,
                        help='Enter track numbers to exclude.')
    parser.add_argument('--include', nargs='+', type=int,
                        help='Enter track numbers to include.')
    parser.add_argument('--limit', default=None, type=int,
                        help='Maximum number of tracks to download.')
    parser.add_argument('--range', nargs=2, type=int,
                        help='Enter range of tracks to download.')
    args = parser.parse_args()
    downloaderObject = downloader.soundcloudDownloader(args)
    if args.include is not None:
        args.include = set(args.include)
    if args.exclude is not None:
        args.exclude = set(args.exclude)
    if args.url == None:
        print "No URL entered."
        sys.exit(0)
    try:
        downloaderObject.Download()
    except KeyboardInterrupt:
        print "\nExiting."
        sys.exit(0)

if __name__ == '__main__':
    main()