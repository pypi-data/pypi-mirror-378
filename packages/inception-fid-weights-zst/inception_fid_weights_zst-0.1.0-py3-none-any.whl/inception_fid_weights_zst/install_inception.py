import os, tempfile, hashlib, shutil
from importlib import resources as ir
import zstandard as zstd

PT_NAME  = "inception-2015-12-05.pt"
PT_SHA256 = "f58cb9b6ec323ed63459aa4fb441fe750cfe39fafad6da5cb504a16f19e958f4"

SHARDS = [('inception_fid_weights_zst_shard01', 'data/shard-01.bin'), ('inception_fid_weights_zst_shard02', 'data/shard-02.bin')]

def _default_target_dir():
    return os.getcwd() if os.name == "nt" else "/tmp"

def _assemble_zst(tmp_path):
    with open(tmp_path, "wb") as out:
        for pkg, res in SHARDS:
            with ir.open_binary(pkg, res) as f:
                shutil.copyfileobj(f, out)

def ensure_inception(target_dir=None):
    out_dir = target_dir or os.environ.get("CLEANFID_INCEPTION_DIR") or _default_target_dir()
    os.makedirs(out_dir, exist_ok=True)
    pt_path = os.path.join(out_dir, PT_NAME)
    if not os.path.exists(pt_path):
        with tempfile.TemporaryDirectory() as td:
            zst_path = os.path.join(td, "inception-2015-12-05.pt.zst")
            _assemble_zst(zst_path)
            dctx = zstd.ZstdDecompressor()
            with open(zst_path, "rb") as fin, open(pt_path, "wb") as fout:
                dctx.copy_stream(fin, fout)

    # 무결성 확인
    h = hashlib.sha256()
    with open(pt_path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    if h.hexdigest() != PT_SHA256:
        try: os.remove(pt_path)
        except Exception: pass
        raise RuntimeError("Inception weight SHA256 mismatch")

    return pt_path

def main():
    print(ensure_inception())
