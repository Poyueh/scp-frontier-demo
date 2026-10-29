"""Reconstruct a tested runtime-only trial from a pinned public release.

Delta transport is not a game modification step: the final bytes must match the
full locally exported and tested build. No private development input is read.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, shutil, tempfile, zlib, stat, zipfile
from pathlib import Path, PurePosixPath
from unpack_release import ALLOWED

MAX_FILE = 128 * 1024 * 1024

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

LEGACY_FILES = {'CC-BY-SA-3.0.txt', 'FONT-LICENSES.txt', 'GODOT-NOTICES.txt', 'LICENSE.txt',
    'README.txt', 'build-info.json', 'credits.html', 'frame-pacing.js', 'guide.html', 'index.html',
    'mobile-shell.js', 'play-v0.0.4.pck', 'play.apple-touch-icon.png', 'play.audio.position.worklet.js',
    'play.audio.worklet.js', 'play.html', 'play.icon.png', 'play.js', 'play.png', 'play.wasm', 'spec/index.html'}

def name_ok(name: str) -> bool:
    if name.startswith('legacy/v0.0.4/'):
        return name.removeprefix('legacy/v0.0.4/') in LEGACY_FILES
    if name in {'spec/index.html', 'spec/style.css', 'spec/reader.js', 'spec/manifest.json', 'social/scp-frontier-brand.png'}:
        return True
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
    actual = {p.relative_to(site).as_posix(): sha(p.read_bytes()) for p in site.rglob('*') if p.is_file()}
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
                source_name = entry.get('source', name)
                if not baseline_name_ok(source_name):
                    raise ValueError('Unsafe baseline source name')
                data = (site/source_name).read_bytes()
            elif entry['mode'] in {'file', 'delta'}:
                parts = entry.get('payloads', [{'path': entry.get('payload'), 'sha256': entry.get('payload_sha256')}])
                packed_parts = []
                total = 0
                for part in parts:
                    payload = root / part['path']
                    if payload.is_symlink() or payload.resolve().parent != (root/'payload').resolve():
                        raise ValueError('Unsafe payload path')
                    block = payload.read_bytes()
                    if sha(block) != part['sha256']:
                        raise ValueError('Payload checksum mismatch')
                    total += len(block)
                    if total > MAX_FILE * 2:
                        raise ValueError('Oversized transport')
                    packed_parts.append(block)
                packed = b''.join(packed_parts)
                source_name = entry.get('source', name)
                if not name_ok(source_name):
                    raise ValueError('Unsafe baseline source name')
                data = packed if entry['mode'] == 'file' else reconstruct((site/source_name).read_bytes(), json.loads(packed))
            else:
                raise ValueError('Unknown file mode')
            if len(data) != entry['size'] or sha(data) != entry['sha256']:
                raise ValueError('Final file mismatch: '+name)
            destination = stage/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        native = (stage/'spec/manifest.json').is_file()
        info = json.loads((stage/('spec/manifest.json' if native else 'build-info.json')).read_text())
        if info['game_version' if native else 'version'] != manifest['version']:
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

def baseline_name_ok(name: str) -> bool:
    path = PurePosixPath(name)
    if not name or str(path) != name or path.is_absolute() or any(p.startswith('.') for p in path.parts) or '\\' in name:
        return False
    if len(path.parts) == 1:
        return path.suffix in ALLOWED
    return (name in {'spec/index.html', 'spec/style.css', 'spec/reader.js', 'spec/manifest.json'}
            or len(path.parts) == 3 and path.parts[:2] == ('spec', 'assets') and path.suffix in {'.png', '.webp'}
            or len(path.parts) == 2 and path.parts[0] == 'social' and path.suffix == '.png')

def install_baseline(archive: Path, site: Path, request: Path) -> None:
    manifest = json.loads(request.read_text())
    expected = manifest['baseline_archive']
    data = archive.read_bytes()
    if len(data) != expected['size'] or sha(data) != expected['sha256']:
        raise ValueError('Pinned baseline archive mismatch')
    if site.exists():
        raise ValueError('Baseline target must not exist')
    inventory = manifest['baseline_files']
    if not inventory or any(not baseline_name_ok(name) for name in inventory):
        raise ValueError('Unsafe baseline inventory')
    stage = Path(tempfile.mkdtemp(prefix='.baseline-', dir=site.parent))
    try:
        with zipfile.ZipFile(archive) as bundle:
            entries = bundle.infolist()
            names = [entry.filename for entry in entries]
            if len(names) != len(set(names)) or sum(e.file_size for e in entries) > 256*1024*1024:
                raise ValueError('Unsafe baseline archive size or duplicates')
            actual = set()
            for entry in entries:
                if stat.S_ISLNK(entry.external_attr >> 16):
                    raise ValueError('Baseline symlink rejected')
                if entry.is_dir():
                    directory = entry.filename.rstrip('/')
                    if directory not in {'spec', 'spec/assets', 'social'}:
                        raise ValueError('Unsafe baseline directory')
                    continue
                name = entry.filename
                if not baseline_name_ok(name) or name not in inventory:
                    raise ValueError('Unexpected baseline member')
                block = bundle.read(entry)
                if sha(block) != inventory[name]:
                    raise ValueError('Baseline member checksum mismatch')
                target = stage/name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(block)
                actual.add(name)
            if actual != set(inventory):
                raise ValueError('Missing baseline member')
        os.replace(stage, site)
    finally:
        if stage.exists():
            shutil.rmtree(stage)

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site', type=Path, required=True)
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--baseline-archive', type=Path)
    a=p.parse_args()
    if a.baseline_archive:install_baseline(a.baseline_archive,a.site,a.request)
    apply_trial(a.site,a.request)
    print('Verified trial installed atomically.')
