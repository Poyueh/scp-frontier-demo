"""Install a checksum-verified artifact-only Web release into an empty Pages site."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ALLOWED={'.html','.js','.css','.json','.png','.svg','.wasm','.pck','.txt','.ico'}

def unpack(release: Path,site: Path,tag: str) -> None:
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+',tag):raise ValueError('Invalid release tag')
    name='SCP-Frontier-Web-'+tag[1:]+'.zip'
    checksums={}
    for line in (release/'SHA256SUMS.txt').read_text().splitlines():
        checksum,filename=line.split()
        if filename in checksums:raise ValueError('Duplicate checksum')
        checksums[filename]=checksum
    archive=release/name
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual!=checksums.get(name):raise ValueError('Release checksum mismatch')
    if site.exists() and any(site.iterdir()):raise ValueError('Site must be empty')
    with zipfile.ZipFile(archive) as bundle:
        entries=bundle.infolist()
        names=[item.filename for item in entries]
        if len(names)!=len(set(names)):raise ValueError('Duplicate archive entries')
        if sum(item.file_size for item in entries)>256*1024*1024:raise ValueError('Unexpected archive size')
        for item in entries:
            path=PurePosixPath(item.filename)
            if (len(path.parts)!=1 or path.is_absolute() or '\\' in item.filename
                or item.filename.startswith('.') or path.suffix not in ALLOWED
                or stat.S_ISLNK(item.external_attr>>16) or item.is_dir()):
                raise ValueError('Not a public runtime file: '+item.filename)
        required={'index.html','play.html','play.js','play.wasm','play.pck','guide.html','credits.html','LICENSE.txt','CC-BY-SA-3.0.txt','FONT-LICENSES.txt','GODOT-NOTICES.txt','build-info.json'}
        if not required.issubset(set(names)):raise ValueError('Incomplete release')
        bundle.testzip() is None or (_ for _ in ()).throw(ValueError('Corrupt archive'))
        site.mkdir(parents=True,exist_ok=True)
        for item in entries:(site/item.filename).write_bytes(bundle.read(item))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--release',type=Path,required=True)
    p.add_argument('--site',type=Path,required=True)
    p.add_argument('--tag',required=True)
    a=p.parse_args();unpack(a.release,a.site,a.tag)
