#!/usr/bin/env python3
"""Download a selected range of publicly readable CZBooks chapters as UTF-8 TXT."""

import argparse
import hashlib
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.title = []
        self.body = []
        self.heading = []
        self.stack = []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get('class', '').split())
        inherited = self.stack[-1][1] if self.stack else set()
        flags = set(inherited)
        if tag in {'script', 'style', 'noscript'}:
            flags.add('hidden')
        if tag == 'title':
            flags.add('title')
        if 'content' in classes:
            flags.add('body')
        if 'name' in classes or tag == 'h1':
            flags.add('heading')
        if 'body' in flags and tag in {'br', 'p', 'div'}:
            self.body.append('\n')
        if tag == 'a':
            self.anchor = [attrs.get('href', ''), []]
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                       'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, flags))

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            self.links.append((self.anchor[0], ''.join(self.anchor[1]).strip()))
            self.anchor = None
        if self.stack and 'body' in self.stack[-1][1] and tag in {'p', 'div'}:
            self.body.append('\n')
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        flags = self.stack[-1][1] if self.stack else set()
        if 'hidden' in flags:
            return
        if self.anchor is not None:
            self.anchor[1].append(data)
        for flag, target in [('title', self.title), ('heading', self.heading),
                             ('body', self.body)]:
            if flag in flags:
                target.append(data)


def parse(html):
    page = Page()
    page.feed(html)
    return page


def book_url(value):
    parts = urlsplit(value)
    if (parts.scheme != 'https' or parts.hostname != 'czbooks.net'
            or parts.username or parts.password or parts.port
            or not re.fullmatch(r'/n/[A-Za-z0-9_-]+/?', parts.path)):
        raise ValueError('URL must be https://czbooks.net/n/BOOK_ID')
    return 'https://czbooks.net' + parts.path.rstrip('/')


def chapters(page, base):
    prefix = urlsplit(base).path.rstrip('/') + '/'
    result, seen = [], set()
    for href, title in page.links:
        url = urljoin(base + '/', href)
        parts = urlsplit(url)
        if (parts.scheme != 'https' or parts.netloc != 'czbooks.net'
                or not parts.path.startswith(prefix)):
            continue
        suffix = parts.path[len(prefix):]
        if not re.fullmatch(r'[A-Za-z0-9_-]+', suffix) or not title:
            continue
        url = 'https://czbooks.net' + parts.path
        if url not in seen:
            result.append({'title': title, 'url': url})
            seen.add(url)
    if not result:
        raise ValueError('No chapter links found; site structure may have changed or access is blocked.')
    return result


def chapter_text(page, fallback_title):
    lines = [line.strip() for line in ''.join(page.body).splitlines()]
    text = '\n\n'.join(line for line in lines if line)
    if not text:
        raise ValueError('No chapter content found; refusing to save an empty chapter.')
    title = ''.join(page.heading).strip() or fallback_title
    return title + '\n\n' + text + '\n'


class Fetcher:
    def __init__(self, delay):
        self.delay = delay
        self.last = None

    def get(self, url):
        if self.last is not None:
            time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
        self.last = time.monotonic()
        request = Request(url, headers={'User-Agent': 'CZBooksRawReader/1.0',
                                        'Accept': 'text/html'})
        with urlopen(request, timeout=30) as response:
            final = urlsplit(response.geturl())
            if final.hostname != 'czbooks.net' or final.scheme != 'https':
                raise ValueError('Unexpected redirect; stopped.')
            data = response.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024:
                raise ValueError('Page is unexpectedly large; stopped.')
            return data.decode(response.headers.get_content_charset() or 'utf-8')


def atomic_write(path, text):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def main(argv=None, fetcher=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='Book index URL, not a chapter URL')
    parser.add_argument('--download', action='store_true', help='Save chapters; otherwise only show the index')
    parser.add_argument('--start', type=int, default=1, help='First position in index (1-based)')
    parser.add_argument('--end', type=int, help='Last position, inclusive; defaults to last chapter')
    parser.add_argument('--delay', type=float, default=3, help='Seconds between requests (minimum 2)')
    parser.add_argument('--output', type=Path, default=Path('raw'), help='Output directory')
    args = parser.parse_args(argv)
    if args.start < 1 or (args.end is not None and args.end < args.start):
        parser.error('Invalid chapter range')
    if not 2 <= args.delay <= 3600:
        parser.error('--delay must be between 2 and 3600 seconds')
    base = book_url(args.url)
    fetcher = fetcher or Fetcher(args.delay)
    page = parse(fetcher.get(base))
    index = chapters(page, base)
    print('Page:', ''.join(page.title).strip())
    print('Chapters:', len(index))
    end = args.end if args.end is not None else len(index)
    if args.start > len(index) or end > len(index):
        raise ValueError('Requested range exceeds the chapter index')
    selected = list(enumerate(index, 1))[args.start - 1:end]
    if not args.download:
        for number, chapter in selected:
            print(f'{number:05d}  {chapter["title"]}  {chapter["url"]}')
        print('Preview only. Check the book title and order, then add --download.')
        return 0
    output = args.output / urlsplit(base).path.split('/')[-1]
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / 'manifest.json'
    manifest = {'book_url': base, 'chapters': {}}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('book_url') != base:
            raise ValueError('Output directory belongs to another book')
    files = []
    for number, chapter in selected:
        key = str(number)
        path = output / f'{number:05d}.txt'
        recorded = manifest['chapters'].get(key, {})
        if path.exists():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if recorded.get('url') != chapter['url'] or recorded.get('sha256') != digest:
                raise ValueError(f'Existing file does not match manifest: {path}; use another output directory.')
            print('Already saved:', path)
        else:
            text = chapter_text(parse(fetcher.get(chapter['url'])), chapter['title'])
            atomic_write(path, text)
            manifest['chapters'][key] = dict(chapter, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            atomic_write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
            print('Saved:', path)
        files.append(path)
    merged = output / f'combined-{args.start:05d}-{end:05d}.txt'
    atomic_write(merged, '\n\n'.join(path.read_text(encoding='utf-8') for path in files))
    print('Combined:', merged)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
        print(f'Stopped: {error}', file=sys.stderr)
        print('Saved chapters are retained. For 403/429, CAPTCHA or login requirements, stop and use the site normally.', file=sys.stderr)
        sys.exit(1)
