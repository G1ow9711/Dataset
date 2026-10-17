"""Download original dataset archives; verify parts and reassembled SHA256."""
import argparse
import hashlib
import json
import pathlib
import time
import urllib.parse
import urllib.request

CHUNK = 4 * 1024 * 1024


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b''):
            h.update(chunk)
    return h.hexdigest()


def checked_name(name):
    if not name or pathlib.PurePosixPath(name).name != name or chr(92) in name or name in ('.', '..'):
        raise ValueError('Invalid payload filename: ' + name)
    return name


def verify(path, item):
    return path.is_file() and path.stat().st_size == item['bytes'] and file_sha256(path) == item['sha256']


def payload_url(item, manifest):
    if item.get('download_url'):
        return item['download_url']
    tag = item.get('release_tag') or manifest['release_tag']
    name = urllib.parse.quote(item.get('asset_name', item['name']))
    if item['name'].endswith('.pdf'):
        return f'https://raw.githubusercontent.com/G1ow9711/Dataset/{tag}/{name}'
    return f'https://github.com/G1ow9711/Dataset/releases/download/{tag}/{name}'


def download_one(item, destination, manifest):
    if destination.exists():
        if verify(destination, item):
            print('Verified existing:', destination, flush=True)
            return
        raise RuntimeError('Existing file differs; move it aside: ' + str(destination))
    temporary = destination.with_name(destination.name + '.partial')
    if temporary.exists() and verify(temporary, item):
        temporary.rename(destination)
        return
    url = payload_url(item, manifest)
    for attempt in range(3):
        offset = temporary.stat().st_size if temporary.exists() else 0
        headers = {'User-Agent': 'Dataset-Verified-Download'}
        if offset:
            headers['Range'] = f'bytes={offset}-'
        print('Downloading:', item['name'], 'offset=', offset, flush=True)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as response:
                status = getattr(response, 'status', None)
                if status == 206:
                    if not response.headers.get('Content-Range', '').startswith(f'bytes {offset}-'):
                        raise RuntimeError('Unexpected HTTP range: ' + item['name'])
                    mode = 'ab'
                else:
                    mode, offset = 'wb', 0
                with temporary.open(mode) as out:
                    total = offset
                    for chunk in iter(lambda: response.read(CHUNK), b''):
                        out.write(chunk)
                        total += len(chunk)
                        if total > item['bytes']:
                            raise RuntimeError('Download exceeds declared size: ' + item['name'])
            break
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
    if not verify(temporary, item):
        raise RuntimeError('Download size or SHA256 mismatch; partial retained: ' + item['name'])
    temporary.rename(destination)
    print('Downloaded and verified:', destination, flush=True)


def download_payload(item, output, manifest):
    destination = output / checked_name(item['name'])
    if destination.exists():
        if verify(destination, item):
            print('Verified existing:', destination, flush=True)
            return
        raise RuntimeError('Existing file differs; move it aside: ' + str(destination))
    if not item.get('parts'):
        download_one(item, destination, manifest)
        return
    parts_dir = output / '.parts' / item['name']
    parts_dir.mkdir(parents=True, exist_ok=True)
    if sum(p['bytes'] for p in item['parts']) != item['bytes']:
        raise ValueError('Part sizes do not sum to archive size')
    paths = []
    for part in item['parts']:
        path = parts_dir / checked_name(part['name'])
        download_one(part, path, manifest)
        paths.append(path)
    temporary = destination.with_name(destination.name + '.partial')
    h, total = hashlib.sha256(), 0
    with temporary.open('wb') as out:
        for path in paths:
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(CHUNK), b''):
                    out.write(chunk)
                    h.update(chunk)
                    total += len(chunk)
    if total != item['bytes'] or h.hexdigest() != item['sha256']:
        raise RuntimeError('Reassembled archive size or SHA256 mismatch; parts retained')
    temporary.rename(destination)
    print('Reassembled and verified:', destination, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path('DataSet'))
    parser.add_argument('--dataset', choices=['all', 'legacy', '129', 'supplement'], default='all')
    parser.add_argument('--verify-only', action='store_true', help='Verify complete archives already downloaded; no network access')
    args = parser.parse_args()
    manifest = json.loads(pathlib.Path(__file__).with_name('manifest.json').read_text(encoding='utf-8'))
    args.output.mkdir(parents=True, exist_ok=True)
    for item in manifest['payload']:
        group = ('129' if item['name'] == '129.zip' else
                 'supplement' if item['name'] == '真值数据（2026-10-15提供）.rar' else 'legacy')
        if args.dataset not in ('all', group):
            continue
        if args.verify_only:
            if not verify(args.output / checked_name(item['name']), item):
                raise RuntimeError('Missing or mismatched payload: ' + item['name'])
            print('Verified:', item['name'], flush=True)
        else:
            download_payload(item, args.output, manifest)


if __name__ == '__main__':
    main()
