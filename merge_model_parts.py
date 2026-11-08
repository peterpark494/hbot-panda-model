"""Merge and verify the downloaded model volumes; uses only Python 3 stdlib."""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Destination tar filename')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    target = args.output or root / manifest['file']
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite: {target}')
    for part in manifest['parts']:
        if Path(part['file']).name != part['file']:
            raise ValueError('Invalid part filename')
        path = root / part['file']
        if not path.is_file() or path.stat().st_size != part['size']:
            raise RuntimeError(f'Missing or incomplete part: {path}')
    temporary = target.with_name(target.name + '.assembling')
    complete = hashlib.sha256()
    total = 0
    with temporary.open('xb') as output:
        for part in manifest['parts']:
            digest = hashlib.sha256()
            with (root / part['file']).open('rb') as source:
                while True:
                    chunk = source.read(16 * 1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
                    digest.update(chunk)
                    complete.update(chunk)
                    total += len(chunk)
            if digest.hexdigest() != part['sha256']:
                raise RuntimeError(f'Corrupt part: {part["file"]}; original parts preserved')
            print('Verified:', part['file'], flush=True)
    if total != manifest['size'] or complete.hexdigest() != manifest['sha256']:
        raise RuntimeError('Combined model checksum mismatch')
    temporary.replace(target)
    print('SHA256_OK', complete.hexdigest())
    print('Model bundle:', target)


if __name__ == '__main__':
    main()
