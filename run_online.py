"""GitHub Actions entry point. Inputs are data, never shell commands."""

import os
import sys

from czbooks_raw import main


def arguments(environ):
    start = int(environ['START_CHAPTER'])
    end = int(environ['END_CHAPTER'])
    if start < 1 or end < start or end - start + 1 > 200:
        raise ValueError('Select between 1 and 200 chapters per run.')
    args = [environ['BOOK_URL'], '--start', str(start), '--end', str(end),
            '--delay', '3', '--output', environ['RAW_OUTPUT']]
    if environ.get('DOWNLOAD_CHAPTERS', 'false').lower() == 'true':
        args.append('--download')
    return args


if __name__ == '__main__':
    try:
        sys.exit(main(arguments(os.environ)))
    except Exception as error:
        print(f'Stopped: {error}', file=sys.stderr)
        sys.exit(1)
