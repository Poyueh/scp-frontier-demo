"""Reconstruct a tested runtime-only trial from a pinned public release.

Delta transport is not a game modification step: the final bytes must match the
full locally exported and tested build. No private development input is read.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, shutil, tempfile, zlib
from pathlib import Path
from unpack_release import ALLOWED

MAX_FILE = 128 * 1024 * 1024

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def name_ok(name: str) -> bool:
    return bool(name) and Path(name).name == name and '\\' not in name and not name.startswith('.') and Path(name).suffix in ALLOWED

def reconstruct(source: bytes, patch: dict) -> bytes:
    if sha(source) != patch['source_sha256'] or len(source) != patch['source_size']:
        raise ValueError('Baseline byte mismatch')
    size = patch['target_size']
    if type(size) is not int or not 0 <= size <= MAX_FILE:
        raise ValueError('Unsafe target size')
    out = bytearray()
    for operation in patch['operations']:
        if set(operation) == {'copy'}:
            offset, length = operation['copy']
            if type(offset) is not int or type(length) is not int or offset < 0 or length < 0 or offset + length > len(source):
                raise ValueError('Unsafe copy range')
            block = source[offset:offset + length]
        elif set(operation) == {'zlib', 'length'}:
            length = operation['length']
            if type(length) is not int or length < 0 or length > size - len(out):
                raise ValueError('Unsafe literal size')
            packed = base64.b64decode(operation['zlib'], validate=True)
            decoder = zlib.decompressobj()
            block = decoder.decompress(packed, length + 1)
            if len(block) != length or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                raise ValueError('Corrupt or oversized literal')
        else:
            raise ValueError('Unknown patch operation')
        if len(out) + len(block) > size:
            raise ValueError('Patch exceeds target size')
        out.extend(block)
    result = bytes(out)
    if len(result) != size or sha(result) != patch['target_sha256']:
        raise ValueError('Reconstructed output mismatch')
    return result

def apply_trial(site: Path, request: Path) -> None:
    manifest = json.loads(request.read_text())
    if manifest.get('format') != 1 or not re.fullmatch(r'\d+\.\d+\.\d+', manifest['version']):
        raise ValueError('Invalid manifest')
    root = request.parent.resolve()
    actual = {p.name: sha(p.read_bytes()) for p in site.iterdir() if p.is_file()}
    if actual != manifest['baseline_files']:
        raise ValueError('Baseline file inventory mismatch')
    if not manifest['files'] or any(not name_ok(n) for n in manifest['files']):
        raise ValueError('Unsafe output name')
    if (root/'payload').is_symlink() or sum(e['size'] for e in manifest['files'].values()) > 256*1024*1024:
        raise ValueError('Unsafe payload directory or total size')
    stage = Path(tempfile.mkdtemp(prefix='.trial-', dir=site.parent))
    try:
        for name, entry in manifest['files'].items():
            if entry['mode'] == 'keep':
                data = (site/name).read_bytes()
            elif entry['mode'] in {'file', 'delta'}:
                relative = entry['payload']
                payload = root / relative
                if payload.is_symlink() or payload.resolve().parent != (root/'payload').resolve():
                    raise ValueError('Unsafe payload path')
                packed = payload.read_bytes()
                if sha(packed) != entry['payload_sha256']:
                    raise ValueError('Payload checksum mismatch')
                source_name = entry.get('source', name)
                if not name_ok(source_name):
                    raise ValueError('Unsafe baseline source name')
                data = packed if entry['mode'] == 'file' else reconstruct((site/source_name).read_bytes(), json.loads(packed))
            else:
                raise ValueError('Unknown file mode')
            if len(data) != entry['size'] or sha(data) != entry['sha256']:
                raise ValueError('Final file mismatch: '+name)
            (stage/name).write_bytes(data)
        info = json.loads((stage/'build-info.json').read_text())
        if info['version'] != manifest['version']:
            raise ValueError('Runtime version mismatch')
        for name in ('LICENSE.txt','CC-BY-SA-3.0.txt','FONT-LICENSES.txt','GODOT-NOTICES.txt','credits.html'):
            if not (stage/name).is_file():
                raise ValueError('Missing license artifact')
        backup = site.with_name(site.name+'.baseline')
        if backup.exists():
            raise ValueError('Unexpected baseline backup exists')
        os.replace(site, backup)
        try:
            os.replace(stage, site)
        except BaseException:
            os.replace(backup, site)
            raise
        shutil.rmtree(backup)
    finally:
        if stage.exists():
            shutil.rmtree(stage)

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site', type=Path, required=True)
    p.add_argument('--request', type=Path, required=True)
    a=p.parse_args();apply_trial(a.site,a.request)
    print('Verified trial installed atomically.')
