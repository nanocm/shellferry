#!/bin/sh
set -eu
mkdir -p "$OFFLINE_PREFIX/bin"
export PATH="$OFFLINE_PREFIX/bin:$PATH"
work=$(mktemp -d)
offline_fetch "https://cdn.porter.sh/download/$PORTER_VERSION/exec-linux-amd64" "$work/exec-linux-amd64"
mkdir -p "$work/$PORTER_VERSION"
mv "$work/exec-linux-amd64" "$work/$PORTER_VERSION/exec-linux-amd64"
python3 - "$work" <<'PY' &
import http.server
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root), **kwargs)
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
(root / 'port').write_text(str(server.server_port))
server.serve_forever()
PY
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true; rm -rf "$work"' EXIT
i=0
while [ ! -s "$work/port" ]; do i=$((i+1)); [ "$i" -lt 100 ] || exit 1; sleep 0.1; done
export PORTER_MIXIN_URL="http://127.0.0.1:$(cat "$work/port")"
export NO_PROXY=127.0.0.1
export no_proxy=127.0.0.1
bash "$OFFLINE_ROOT/upstream/install.sh" "$@"
ln -sf "$PORTER_HOME/porter" "$OFFLINE_PREFIX/bin/porter"
