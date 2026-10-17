"""Offline controls for integrity, HTTP resume, and original-byte assembly."""
import hashlib
import http.server
import pathlib
import tempfile
import threading
import unittest
import download


def entry(path, name=None):
    data = path.read_bytes()
    return dict(name=name or path.name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), download_url=path.as_uri())


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.output = self.root / 'output'
        self.output.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_single_payload_and_existing_file(self):
        source = self.root / 'data.rar'; source.write_bytes(bytes(range(256)))
        item = entry(source)
        download.download_payload(item, self.output, {})
        item['download_url'] = 'https://invalid.invalid/unnecessary'
        download.download_payload(item, self.output, {})
        self.assertEqual((self.output / source.name).read_bytes(), source.read_bytes())

    def test_split_exact_assembly_with_existing_partial(self):
        body = b'original zip bytes' * 31
        parts = []
        for index, value in enumerate([body[:171], body[171:400], body[400:]]):
            path = self.root / f'part{index}'; path.write_bytes(value); parts.append(entry(path))
        part_dir = self.output / '.parts/129.zip'; part_dir.mkdir(parents=True)
        (part_dir / 'part0.partial').write_bytes(body[:20])
        item = dict(name='129.zip', bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), parts=parts)
        download.download_payload(item, self.output, {})
        self.assertEqual((self.output / '129.zip').read_bytes(), body)

    def test_corrupt_download_never_published(self):
        source = self.root / 'bad.rar'; source.write_bytes(b'bad')
        item = entry(source); item['sha256'] = hashlib.sha256(b'new').hexdigest()
        with self.assertRaisesRegex(RuntimeError, 'SHA256 mismatch'):
            download.download_payload(item, self.output, {})
        self.assertFalse((self.output / source.name).exists())

    def test_reassembly_mismatch_never_published(self):
        source = self.root / 'part0'; source.write_bytes(b'valid part')
        item = dict(name='129.zip', bytes=10, sha256='0' * 64, parts=[entry(source)])
        with self.assertRaisesRegex(RuntimeError, 'Reassembled archive'):
            download.download_payload(item, self.output, {})
        self.assertFalse((self.output / '129.zip').exists())
        self.assertTrue((self.output / '.parts/129.zip/part0').exists())

    def test_existing_destination_is_not_overwritten(self):
        source = self.root / 'data.zip'; source.write_bytes(b'expected')
        dest = self.output / 'data.zip'; dest.write_bytes(b'user content')
        with self.assertRaisesRegex(RuntimeError, 'Existing file differs'):
            download.download_payload(entry(source), self.output, {})
        self.assertEqual(dest.read_bytes(), b'user content')

    def test_http_range_resume(self):
        body = b'abcdefghij' * 17
        seen = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(self.headers.get('Range'))
                start = int(self.headers['Range'].split('=')[1].split('-')[0])
                self.send_response(206)
                self.send_header('Content-Range', f'bytes {start}-{len(body)-1}/{len(body)}')
                self.send_header('Content-Length', str(len(body)-start))
                self.end_headers()
                self.wfile.write(body[start:])
            def log_message(self, *args):
                pass
        with http.server.HTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            try:
                item = dict(name='resume.zip', bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                            download_url=f'http://127.0.0.1:{server.server_port}/archive')
                (self.output / 'resume.zip.partial').write_bytes(body[:23])
                download.download_payload(item, self.output, {})
            finally:
                server.shutdown(); thread.join()
        self.assertEqual(seen, ['bytes=23-'])
        self.assertEqual((self.output / 'resume.zip').read_bytes(), body)

    def test_legacy_url_preserved(self):
        item = dict(name='旧.zip', asset_name='old.zip', release_tag='dataset-20261008')
        self.assertIn('/dataset-20261008/old.zip', download.payload_url(item, {'release_tag':'dataset-20261017'}))


if __name__ == '__main__':
    unittest.main()

