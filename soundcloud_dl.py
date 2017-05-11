from .downloader import downloader
import sys, argparse, os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', default=None, type=str, nargs='?',
        help='URL to download tracks from. (Positional Argument)')
    parser.add_argument('-d', '--dir', default=os.getcwd(), type=str,
        help='Directory to save tracks in. Default value is the current working directory.')
    parser.add_argument('-a', '--all', default=False, action='store_true',
        help='Download all tracks.(Uploads and likes)')
    parser.add_argument('-l', '--likes', default=False, action='store_true',
        help='Download only liked tracks.')
    parser.add_argument('-e', '--exclude', nargs='+', type=int,
        help='Enter track numbers to exclude.')
    parser.add_argument('-i', '--include', nargs='+', type=int,
        help='Enter track numbers to include.')
    parser.add_argument('--limit', default=None, type=int,
        help='Maximum number of tracks to download.')
    parser.add_argument('-r', '--range', nargs=2, type=int,
        help='Enter range of tracks to download.')
    parser.add_argument('-t', '--top', nargs='?', type=int, const=10,
        help='Downloads the top 10 tracks from all genres')
    parser.add_argument('-n', '--new', nargs='?', type=int, const=10,
        help='Downloads 10 new tracks from all genres')
    parser.add_argument('-g', '--genre', nargs='?', type=str, default='all-music',
        help='use with --top to get top tracks from a specific genre')
    args = parser.parse_args()
    downloaderObject = downloader.soundcloudDownloader(args)
    args.url.replace('\\', '/')
    if args.include is not None:
        args.include = set(args.include)
    if args.exclude is not None:
        args.exclude = set(args.exclude)
    try:
        downloaderObject.Download()
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)

if __name__ == '__main__':
    main()