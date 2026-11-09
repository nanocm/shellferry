"""Apply the standard offline verifier to exact literal SDKMAN prefix cases."""
from pathlib import Path
import hashlib
import json
import shlex
import sys

root = Path(__file__).resolve().parent
repo = root.parents[2]
sys.path.insert(0, str(repo / 'skills/shellferry/scripts'))
import verify

archive = root / 'sdkman-5.24.0-temurin21-offline.tar.gz'
original_harness = verify.HARNESS
cases = {
    'literal-home-spaces-quote': "/tmp/offline-home/literal $HOME  user's sdk",
    'shell-metacharacters': '/tmp/offline-home/literal $(printf SUBSTITUTION_RAN) `printf BACKTICK_RAN` "quoted" back\\slash',
}
results = []
for label, prefix in cases.items():
    verify.HARNESS = original_harness.replace('prefix="$HOME/prefix with spaces"', 'prefix=' + shlex.quote(prefix))
    verify.HARNESS = verify.HARNESS.replace('sh smoke.sh "$prefix"', 'sh smoke.sh "$prefix"\ncat "$HOME/.bashrc"')
    output = root / ('report-prefix-' + label + '.json')
    sys.argv = ['verify.py', str(archive), '--engine', 'podman', '--image', 'localhost/shellferry-sdkman:ubuntu22', '--output', str(output), '--timeout', '240']
    code = verify.main()
    report = json.loads(output.read_text(encoding='utf-8'))
    report['custom_prefix'] = prefix
    report['checks'] = [c for c in report['checks'] if c != 'path with spaces'] + ['literal shell characters in prefix', 'fresh shell restores exact SDKMAN_DIR', 'javac compiles and java executes with exact prefix']
    report['supplemental_harness'] = {'path': 'work/expansion105/sdkman/verify_special_prefixes.py', 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'rendered_harness_sha256': hashlib.sha256(verify.HARNESS.encode()).hexdigest()}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    results.append({'case': label, 'prefix': prefix, 'status': report['status'], 'report': output.name, 'archive_sha256': report['archive_sha256'], 'elapsed_seconds': report['elapsed_seconds']})
    if code:
        break
(root / 'prefix-results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8', newline='\n')
raise SystemExit(code)
