"""Download the published dataset snapshot and verify every payload SHA256."""
import argparse
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request


def file_sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path('DataSet'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(pathlib.Path(__file__).with_name('manifest.json').read_text(encoding='utf-8'))
    for item in manifest['payload']:
        destination = args.output / item['name']
        if destination.is_file():
            actual = file_sha256(destination)
            if actual == item['sha256']:
                print('Verified existing:', destination)
                continue
            raise RuntimeError('Existing file differs; move it aside before downloading: ' + str(destination))
        if item['name'].endswith('.pdf'):
            url = 'https://raw.githubusercontent.com/G1ow9711/Dataset/' + manifest['release_tag'] + '/' + urllib.parse.quote(item['name'])
        else:
            url = 'https://github.com/G1ow9711/Dataset/releases/download/' + manifest['release_tag'] + '/' + urllib.parse.quote(item.get('asset_name', item['name']))
        temporary = destination.with_suffix(destination.suffix + '.partial')
        h = hashlib.sha256()
        total = 0
        request = urllib.request.Request(url, headers={'User-Agent': 'Dataset-Verified-Download'})
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open('wb') as output:
            for chunk in iter(lambda: response.read(4 * 1024 * 1024), b''):
                output.write(chunk)
                h.update(chunk)
                total += len(chunk)
        if total != item['bytes'] or h.hexdigest() != item['sha256']:
            raise RuntimeError('Download size or SHA256 mismatch: ' + item['name'])
        temporary.rename(destination)
        print('Downloaded and verified:', destination)


if __name__ == '__main__':
    main()
