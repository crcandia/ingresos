"""Package only user-facing sources and outputs, excluding temporary previews."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
files=[]
for path in ROOT.rglob('*'):
    if not path.is_file():
        continue
    rel=path.relative_to(ROOT)
    if any(x in rel.parts for x in ['.git','__pycache__','node_modules','render_temporal']):
        continue
    if path.name in ['MANIFEST_SHA256.json'] or path.suffix in ['.pyc']:
        continue
    if rel.parts[0]=='qa' and path.suffix not in ['.py','.cjs','.json','.md','.txt']:
        continue
    files.append(path)
files.sort()
manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
(ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
target=ROOT.parent/'ESI2025_dashboard_reproducible.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p in files+[ROOT/'MANIFEST_SHA256.json']:
        archive.write(p,arcname=str(p.relative_to(ROOT.parent)))
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for name,metadata in manifest.items():
        assert hashlib.sha256(archive.read(ROOT.name+'/'+name)).hexdigest()==metadata['sha256']
print(json.dumps({'file':str(target),'files':len(files)+1,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
