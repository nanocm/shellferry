#!/bin/sh
set -eu
mkdir -p "$HOME/workspace" "$HOME/code-data" "$HOME/extensions"
printf 'offline editor workspace\n' > "$HOME/workspace/example.txt"
"$OFFLINE_PREFIX/bin/code-server" --version
"$OFFLINE_PREFIX/bin/code-server" --bind-addr 127.0.0.1:18080 --auth none --disable-telemetry --disable-update-check --user-data-dir "$HOME/code-data" --extensions-dir "$HOME/extensions" "$HOME/workspace" > "$HOME/code-server.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT HUP INT TERM
if ! "$OFFLINE_PREFIX/lib/code-server-4.145.2/lib/node" <<'JS'
const http = require('node:http');
const assert = require('node:assert/strict');
const origin = 'http://127.0.0.1:18080';
function get(path, redirects = 0) {
  return new Promise((resolve, reject) => {
    const req = http.get(new URL(path, origin), res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirects < 5) {
        res.resume();
        const target = new URL(res.headers.location, origin);
        assert.equal(target.origin, origin);
        get(target.pathname + target.search, redirects + 1).then(resolve, reject);
        return;
      }
      let body = '';
      res.setEncoding('utf8');
      res.on('data', data => body += data);
      res.on('end', () => resolve({status: res.statusCode, body}));
    });
    req.setTimeout(2000, () => req.destroy(new Error('Local HTTP timeout')));
    req.on('error', reject);
  });
}
(async () => {
  let last;
  for (let attempt = 0; attempt < 100; attempt++) {
    try {
      const health = await get('/healthz');
      assert.equal(health.status, 200);
      assert.ok(['alive', 'expired'].includes(JSON.parse(health.body).status));
      const page = await get('/');
      assert.equal(page.status, 200);
      assert.match(page.body, /<html/i);
      assert.match(page.body, /workbench|vscode/i);
      console.log('Offline editor HTTP health and workbench passed');
      return;
    } catch (error) { last = error; }
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw last;
})().catch(error => { console.error(error.message); process.exit(1); });
JS
then
  cat "$HOME/code-server.log"
  exit 1
fi
kill "$pid"
wait "$pid" || true
trap - EXIT HUP INT TERM
