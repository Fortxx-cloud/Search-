"""Auto-update wrapper. Download latest ZIP from GitHub, then run main.py."""
import glob
import io
import os
import shutil
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

GITHUB_ZIP = os.getenv(
    "GITHUB_ZIP_URL",
    "https://github.com/Fortxx-cloud/Search-/archive/refs/heads/main.zip",
)
KEEP = {".git", ".env", "__pycache__", ".last_update", "search.db"}


def download_update():
    try:
        print(f"[start] fetching update: {GITHUB_ZIP}")
        data = urllib.request.urlopen(GITHUB_ZIP, timeout=30).read()
        z = zipfile.ZipFile(io.BytesIO(data))
        tmp = "/tmp/pusat_update"
        if os.path.exists(tmp):
            shutil.rmtree(tmp)
        z.extractall(tmp)

        src_candidates = glob.glob(f"{tmp}/*/")
        if not src_candidates:
            print("[start] no folder in ZIP")
            return
        src = src_candidates[0]

        copied = 0
        for item in os.listdir(src):
            if item in KEEP:
                continue
            s = os.path.join(src, item)
            d = os.path.join(ROOT, item)
            try:
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
                copied += 1
            except Exception as e:
                print(f"[start] skip {item}: {e}")

        print(f"[start] updated {copied} items")
    except Exception as e:
        print(f"[start] update failed (using existing): {e}")


download_update()
sys.path.insert(0, ROOT)
exec(open(os.path.join(ROOT, "main.py")).read())
