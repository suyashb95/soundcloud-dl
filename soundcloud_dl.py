from downloader.utils import set_api_key

import sys, argparse, os

def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument('-t', '--top', action='store_true', default=False,
        help='Downloads the top 10 tracks across all genres')
    group.add_argument('-n', '--new', action='store_true', default=False,
        help='Downloads 10 new tracks across all genres')
    group.add_argument('-u', '--url', default=None, type=str, nargs='?',
        help='URL to download tracks from')

    parser.add_argument('--set-api-key', type=str,
        help='sets the soundcloud API key')
    parser.add_argument('-s', '--similar', action='store_true', default=False,
        help='Downloads 10 tracks similar to the track in the URL')
    parser.add_argument('-d', '--dir', default=os.getcwd(), type=str,
        help='Directory to save tracks in. Defaults to current working directory')

    parser.add_argument('-a', '--all', default=False, action='store_true',
        help='Download all tracks (Uploads and likes)')
    parser.add_argument('-l', '--likes', default=False, action='store_true',
        help='Download only liked tracks.')

    parser.add_argument('-e', '--exclude', nargs='+', type=int,
        help='Enter track numbers to exclude.')
    parser.add_argument('-i', '--include', nargs='+', type=int,
        help='Enter track numbers to include')
    parser.add_argument('--limit', type=int,
        help='Maximum number of tracks to download')
    parser.add_argument('-r', '--range', nargs=2, type=int,
        help='Enter range of tracks to download.')

    parser.add_argument('-g', '--genre', nargs='?', type=str, default='all-music',
        help='use with --top to get top tracks from a specific genre')

    args = parser.parse_args()
    
    if args.set_api_key:
        set_api_key(args.set_api_key)
        return

    if args.similar and not args.url:
        print("Track URL is needed to get similar tracks")
        return

    if not any([args.url, args.top, args.new]):
        print("At least one of the following args is required -n/--new -t/--top or -u/--url")
        return                
    
    from downloader import downloader

    d = downloader.SoundcloudDownloader(args)
    if args.include:
        args.include = set(args.include)
    if args.exclude:
        args.exclude = set(args.exclude)

    try:
        d.main()
    except KeyboardInterrupt:
        print("\nExiting")
        sys.exit(0)

if __name__ == '__main__':
    main()