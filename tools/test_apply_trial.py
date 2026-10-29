import base64, copy, hashlib, json, tempfile, unittest, zlib
from pathlib import Path
from apply_trial import reconstruct, sha, name_ok, apply_trial

def literal(data):
    return {'zlib':base64.b64encode(zlib.compress(data)).decode(),'length':len(data)}

class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.source=b'old-BEGIN-unchanged-END'
        self.target=b'new-BEGIN-unchanged-FIN'
        self.patch={'source_size':len(self.source),'source_sha256':sha(self.source),'target_size':len(self.target),
                    'target_sha256':sha(self.target),'operations':[literal(b'new'),{'copy':[3,17]},literal(b'FIN')]}
    def test_exact_reconstruction(self):
        self.assertEqual(reconstruct(self.source,self.patch),self.target)
    def test_corrupt_baseline(self):
        with self.assertRaises(ValueError):reconstruct(self.source+b'x',self.patch)
    def test_wrong_final_hash(self):
        self.patch['target_sha256']='0'*64
        with self.assertRaises(ValueError):reconstruct(self.source,self.patch)
    def test_missing_segment(self):
        self.patch['operations'].pop()
        with self.assertRaises(ValueError):reconstruct(self.source,self.patch)
    def test_corrupt_literal(self):
        self.patch['operations'][0]['zlib']='AAAA'
        with self.assertRaises((ValueError,zlib.error)):reconstruct(self.source,self.patch)
    def test_range_outside_baseline(self):
        self.patch['operations'][1]['copy']=[-1,17]
        with self.assertRaises(ValueError):reconstruct(self.source,self.patch)
    def test_oversized_literal(self):
        self.patch['operations'][0]['zlib']=literal(b'x'*1000)['zlib']
        with self.assertRaises(ValueError):reconstruct(self.source,self.patch)
    def test_unknown_operation(self):
        self.patch['operations']=[{'execute':'echo nope'}]
        with self.assertRaises(ValueError):reconstruct(self.source,self.patch)
    def test_unsafe_names(self):
        for name in ['../x.png','/x.png','x/y.png','.git','code.py','a\\b.png']:
            self.assertFalse(name_ok(name),name)
    def test_atomic_missing_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();(site/'keep.txt').write_bytes(b'unchanged')
            request=root/'request.json';request.write_text(json.dumps({'format':1,'version':'0.0.3',
                'baseline_files':{'keep.txt':sha(b'unchanged')},'files':{'play.pck':{'mode':'file',
                'payload':'payload/missing.bin','payload_sha256':'0'*64,'size':1,'sha256':'0'*64}}}))
            with self.assertRaises(FileNotFoundError):apply_trial(site,request)
            self.assertEqual((site/'keep.txt').read_bytes(),b'unchanged')
            self.assertEqual(list(root.glob('.trial-*')),[])
    def test_atomic_corrupt_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();(site/'keep.txt').write_bytes(b'unchanged')
            payload=root/'payload';payload.mkdir();(payload/'play.pck').write_bytes(b'bad')
            request=root/'request.json';request.write_text(json.dumps({'format':1,'version':'0.0.3',
                'baseline_files':{'keep.txt':sha(b'unchanged')},'files':{'play.pck':{'mode':'file',
                'payload':'payload/play.pck','payload_sha256':sha(b'good'),'size':4,'sha256':sha(b'good')}}}))
            with self.assertRaisesRegex(ValueError,'Payload checksum mismatch'):apply_trial(site,request)
            self.assertEqual((site/'keep.txt').read_bytes(),b'unchanged')
            self.assertEqual(list(root.glob('.trial-*')),[])
    def test_complete_atomic_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);site=root/'site';site.mkdir();payload=root/'payload';payload.mkdir()
            names=['LICENSE.txt','CC-BY-SA-3.0.txt','FONT-LICENSES.txt','GODOT-NOTICES.txt','credits.html']
            for name in names:(site/name).write_bytes(b'license')
            (site/'build-info.json').write_text('{"version":"0.0.2"}')
            (site/'play.pck').write_bytes(self.source)
            baseline={p.name:sha(p.read_bytes()) for p in site.iterdir()}
            files={n:{'mode':'keep','size':7,'sha256':sha(b'license')} for n in names}
            info=b'{"version":"0.0.3"}';(payload/'build-info.json').write_bytes(info)
            patch=json.dumps(self.patch).encode();(payload/'play.pck.delta.json').write_bytes(patch)
            for name,data,mode,pdata,pname in [('build-info.json',info,'file',info,'build-info.json'),('play.pck',self.target,'delta',patch,'play.pck.delta.json')]:
                files[name]={'mode':mode,'size':len(data),'sha256':sha(data),'payload':'payload/'+pname,'payload_sha256':sha(pdata)}
            files['play-v0.0.3.pck']=files.pop('play.pck');files['play-v0.0.3.pck']['source']='play.pck'
            request=root/'current.json';request.write_text(json.dumps({'format':1,'version':'0.0.3','baseline_files':baseline,'files':files}))
            apply_trial(site,request)
            self.assertEqual((site/'play-v0.0.3.pck').read_bytes(),self.target)
            self.assertEqual(set(p.name for p in site.iterdir()),set(files))
            self.assertFalse((root/'site.baseline').exists())

if __name__=='__main__':unittest.main()
