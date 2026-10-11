"""Restore a public Watch Collection source release into a NEW directory.

This script only fetches and validates source files. It never executes the app,
installs dependencies, signs in, or creates a Site. The recipient's GPT owns those steps.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import urllib.parse
import urllib.request

BASE = 'https://raw.githubusercontent.com/jamm2nd/watch-collection/main/'
LIMIT = 24 * 1024 * 1024
PART_LIMIT = 400 * 1024
BLOCKED = {'.git', 'node_modules', 'dist', '.sites-runtime', '.wrangler', '__pycache__'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url, limit):
    with urllib.request.urlopen(url, timeout=60) as response:
        if urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(url).netloc:
            raise ValueError('Unexpected redirect; installation source was not retrieved.')
        result = response.read(limit + 1)
    if len(result) > limit:
        raise ValueError('Source exceeded the expected size limit.')
    return result


def read_source(manifest, directory=None):
    source = manifest['source']
    filename = source['file']
    if not re.fullmatch(r'watch-collection-1\.0-[a-f0-9]{16}\.json', filename):
        raise ValueError('Unexpected source filename.')
    if type(source['bytes']) is not int or not 0 < source['bytes'] <= LIMIT:
        raise ValueError('Invalid source size.')
    if 'parts' not in source:
        return (Path(directory) / filename).read_bytes() if directory else fetch(BASE + filename, LIMIT)
    parts = source['parts']
    if not isinstance(parts, list) or not 1 <= len(parts) <= 64:
        raise ValueError('Invalid source part count.')
    total = 0
    seen = set()
    for index, part in enumerate(parts, 1):
        expected = f'{filename[:-5]}.part-{index:03d}.txt'
        name = part.get('file') if isinstance(part, dict) else None
        if name != expected or name in seen:
            raise ValueError('Unsafe, duplicate, or unordered source part filename.')
        if type(part.get('bytes')) is not int or not 0 < part['bytes'] <= PART_LIMIT:
            raise ValueError('Invalid source part size.')
        if not isinstance(part.get('sha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', part['sha256']):
            raise ValueError('Invalid source part checksum.')
        total += part['bytes']
        seen.add(name)
    if total != source['bytes'] or total > LIMIT:
        raise ValueError('Source part total size mismatch.')
    result = []
    for part in parts:
        raw = ((Path(directory) / part['file']).read_bytes() if directory
               else fetch(BASE + part['file'], part['bytes']))
        if len(raw) != part['bytes'] or sha(raw) != part['sha256']:
            raise ValueError(f"Invalid source part: {part['file']}")
        result.append(raw)
    return b''.join(result)


def validate(manifest, raw):
    if manifest.get('format') != 'watch-collection-manifest-v1':
        raise ValueError('Unrecognized manifest.')
    source = manifest['source']
    if len(raw) != source['bytes'] or sha(raw) != source['sha256']:
        raise ValueError('The source checksum does not match the manifest.')
    bundle = json.loads(raw)
    if bundle.get('format') != 'watch-collection-source-v1' or bundle.get('version') != manifest['version']:
        raise ValueError('Unrecognized source format or mismatched version.')
    files = bundle['files']
    if not 1 <= len(files) <= 5000 or len(files) != manifest['file_count']:
        raise ValueError('Invalid source file count.')
    expected = {f['path']: (f['bytes'], f['sha256']) for f in manifest['files']}
    if len(expected) != len(files):
        raise ValueError('Missing or duplicate manifest entries.')
    result = {}
    folded_paths = set()
    total = 0
    for f in files:
        name = f['path']
        path = PurePosixPath(name)
        if (not isinstance(name, str) or len(name) > 512 or path.is_absolute()
                or path.as_posix() != name or any(p in {'', '.', '..'} for p in name.split('/'))
                or any(p in BLOCKED or p.startswith('.env') for p in path.parts)
                or any(c in name for c in ('\\', ':', '\x00'))
                or name.casefold() in folded_paths or f.get('encoding') != 'base64'):
            raise ValueError('Unsafe or duplicate source path.')
        if type(f['bytes']) is not int or not 0 <= f['bytes'] <= LIMIT:
            raise ValueError('Invalid file size.')
        data = base64.b64decode(f['content'], validate=True)
        if len(data) != f['bytes'] or sha(data) != f['sha256'] or expected.get(name) != (f['bytes'], f['sha256']):
            raise ValueError(f'Invalid source file: {name}')
        total += len(data)
        if total > LIMIT:
            raise ValueError('Decoded source exceeded size limit.')
        result[name] = data
        folded_paths.add(name.casefold())
    if total != manifest['total_file_bytes']:
        raise ValueError('Source total size mismatch.')
    for name in result:
        if any(parent.as_posix() in result for parent in PurePosixPath(name).parents):
            raise ValueError('Conflicting file and directory paths.')
    if json.loads(result['.openai/hosting.json']) != {'d1': 'DB', 'r2': 'PHOTOS'}:
        raise ValueError('The application must not contain another Site identity.')
    return result


def main():
    global BASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True)
    parser.add_argument('--base-url', choices=[BASE, 'https://watch-collection-v1.jamm2nd.chatgpt.site/source/'], default=BASE, help='Choose a published source origin permitted by your environment.')
    parser.add_argument('--manifest-file', help='Use a manifest already fetched by your available tools.')
    parser.add_argument('--bundle-file', help='Use the source JSON already fetched by your available tools.')
    parser.add_argument('--source-directory', help='Read manifest and source parts from a cloned release directory.')
    args = parser.parse_args()
    BASE = args.base_url
    if args.bundle_file and (not args.manifest_file or args.source_directory):
        parser.error('Provide --bundle-file with --manifest-file, without --source-directory.')
    if args.manifest_file and not (args.bundle_file or args.source_directory):
        parser.error('Provide --manifest-file with --bundle-file or --source-directory.')
    target = Path(args.destination).absolute()
    if target.exists() or target.is_symlink():
        raise ValueError('Choose a new, nonexistent destination. Existing directories are never overwritten.')
    if not target.parent.is_dir():
        raise ValueError('The destination parent directory must already exist.')
    manifest_raw = (Path(args.manifest_file).read_bytes() if args.manifest_file
                    else (Path(args.source_directory) / 'manifest.json').read_bytes() if args.source_directory
                    else fetch(BASE + 'manifest.json', 2 * 1024 * 1024))
    manifest = json.loads(manifest_raw)
    filename = manifest['source']['file']
    if not re.fullmatch(r'watch-collection-1\.0-[a-f0-9]{16}\.json', filename):
        raise ValueError('Unexpected source filename.')
    raw = Path(args.bundle_file).read_bytes() if args.bundle_file else read_source(manifest, args.source_directory)
    if len(raw) > LIMIT:
        raise ValueError('Source exceeded size limit.')
    files = validate(manifest, raw)
    target.mkdir()
    for name, data in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as output:
            output.write(data)
    print(json.dumps({'restored': len(files), 'destination': str(target), 'version': manifest['version']}))


if __name__ == '__main__':
    main()
