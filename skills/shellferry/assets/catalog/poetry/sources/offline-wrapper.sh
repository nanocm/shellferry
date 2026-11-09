#!/bin/sh
set -eu
python3 -c 'import sys,venv,ensurepip; assert sys.version_info[:2] == (3,10), "requires Python 3.10"'
python3 - <<'PY'
import os,hashlib,difflib,pathlib
root=pathlib.Path(os.environ["OFFLINE_ROOT"]); target=pathlib.Path(os.environ["OFFLINE_PREFIX"]); target.mkdir(parents=True,exist_ok=True)
raw=(root/"resources/installer.py").read_bytes()
assert hashlib.sha256(raw).hexdigest()=='75745ca71373a7b22fa150953543f03d826a52f8e4bc4350328a33bddd668026'
text=raw.decode(); old='        metadata = json.loads(self._get(self.METADATA_URL).decode())'; new='        metadata = {"releases": {"2.5.1": []}}'
assert text.count(old)==1, "upstream patch anchor changed"
converted=text.replace(old,new)
(target/"offline-installer.py").write_text(converted)
(target/"offline-installer.diff").write_text("".join(difflib.unified_diff(text.splitlines(True),converted.splitlines(True),fromfile="upstream/installer.py",tofile="offline-installer.py")))
PY
python3 "$OFFLINE_PREFIX/offline-installer.py" --version 2.5.1 --yes
