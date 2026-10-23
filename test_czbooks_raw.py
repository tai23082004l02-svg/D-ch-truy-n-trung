import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from czbooks_raw import book_url, chapter_text, chapters, main, parse
from run_online import arguments


BASE = 'https://czbooks.net/n/s6lf47'
INDEX = '''<title>測試小說</title><ul class="chapter-list">
<li><a href="/n/s6lf47/c1">第一章</a></li>
<li><a href="/n/s6lf47/c2">第二章</a></li>
<li><a href="/n/s6lf47/c1">重複</a></li>
<li><a href="https://example.com/n/s6lf47/c3">廣告</a></li></ul>'''
CHAPTER = '''<div class="name">第一章</div><div class="content">
第一行<br>第二行 &amp; 文字<p>第三行</p><script>advert()</script></div>
<footer>不要保存</footer>'''


class FakeFetcher:
    def __init__(self):
        self.calls = []

    def get(self, url):
        self.calls.append(url)
        return INDEX if url == BASE else CHAPTER


class RawTests(unittest.TestCase):
    def test_online_range_and_preview_default(self):
        environ = {'BOOK_URL': BASE, 'START_CHAPTER': '1',
                   'END_CHAPTER': '2', 'RAW_OUTPUT': '/tmp/raw'}
        self.assertNotIn('--download', arguments(environ))
        environ['DOWNLOAD_CHAPTERS'] = 'true'
        self.assertIn('--download', arguments(environ))
        for start, end in [('0', '2'), ('2', '1'), ('1', '201')]:
            environ.update(START_CHAPTER=start, END_CHAPTER=end)
            with self.assertRaises(ValueError):
                arguments(environ)

    def test_index_preserves_order_and_filters_duplicates_and_other_hosts(self):
        result = chapters(parse(INDEX), BASE)
        self.assertEqual([c['url'] for c in result], [BASE + '/c1', BASE + '/c2'])

    def test_body_excludes_scripts_and_navigation_and_keeps_lines(self):
        self.assertEqual(chapter_text(parse(CHAPTER), 'fallback'),
                         '第一章\n\n第一行\n\n第二行 & 文字\n\n第三行\n')

    def test_empty_body_is_error(self):
        with self.assertRaises(ValueError):
            chapter_text(parse('<title>Access denied</title>'), 'chapter')

    def test_only_supported_book_urls(self):
        for url in ['http://czbooks.net/n/book', 'https://evil.test/n/book',
                    BASE + '/c1']:
            with self.assertRaises(ValueError):
                book_url(url)

    def test_download_resume_and_modified_file_protection(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            args = [BASE, '--download', '--end', '2', '--output', directory]
            first = FakeFetcher()
            self.assertEqual(main(args, first), 0)
            self.assertEqual(len(first.calls), 3)
            output = Path(directory) / 's6lf47'
            self.assertEqual((output / 'combined-00001-00002.txt').read_text().count('第一行'), 2)
            second = FakeFetcher()
            self.assertEqual(main(args, second), 0)
            self.assertEqual(second.calls, [BASE])
            (output / '00001.txt').write_text('user edit')
            with self.assertRaises(ValueError):
                main(args, FakeFetcher())
            self.assertEqual((output / '00001.txt').read_text(), 'user edit')

    def test_preview_does_not_download(self):
        with contextlib.redirect_stdout(io.StringIO()):
            fetcher = FakeFetcher()
            self.assertEqual(main([BASE], fetcher), 0)
            self.assertEqual(fetcher.calls, [BASE])


if __name__ == '__main__':
    unittest.main()
