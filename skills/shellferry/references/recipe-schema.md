# Conversion recipe schema 1

`convert.py` performs explicit file transformations. It does not infer shell semantics or run the entrypoint during a build. The destination directory must not already exist; a failed build does not leave a complete artifact.

```json
{
  "schema": 1,
  "name": "tool",
  "version": "1.2.3",
  "target": "linux-x86_64",
  "shell": "sh",
  "entrypoint": "upstream/install.sh",
  "scripts": [
    {
      "path": "upstream/install.sh",
      "url": "https://example.org/install.sh",
      "source": "sources/install.sh",
      "sha256": "64-character-actual-sha256",
      "patches": [
        {
          "old": "curl -fsSL \"$url\" -o \"$archive\"",
          "new": "offline_fetch \"$url\" \"$archive\"",
          "count": 1
        }
      ]
    }
  ],
  "resources": [
    {
      "url": "https://example.org/releases/1.2.3/tool-linux-x64.tar.gz",
      "path": "resources/tool-linux-x64.tar.gz",
      "sha256": "64-character-actual-sha256",
      "checksum_source": "official-release-checksums",
      "aliases": ["https://example.org/releases/latest/tool-linux-x64.tar.gz"]
    }
  ],
  "env": {"TOOL_HOME": "{prefix}", "TOOL_VERSION": "1.2.3"},
  "args": ["--no-modify-path"],
  "repeat_args": ["--force"],
  "requires": ["sh", "tar", "gzip"],
  "smoke": [["{prefix}/bin/tool", "--version"]],
  "notes": ["Description of changes and the intended installation scope."]
}
```

The example domains and digests are schema placeholders; replace them with real values. `assets/catalog/` contains 106 pinned recipes for 105 software packages with recorded build and installation tests.

Field conventions:

- `target`: `linux-x86_64`, `linux-aarch64`, their `-musl` variants, or `darwin-x86_64`/`darwin-aarch64`. Declaring a target does not establish test coverage.
- `default_prefix`: defaults to `{home}/.local`; may be set to `{home}/.bun` or another location. Optional `default_prefix_env` names an upstream install-directory variable such as `BUN_INSTALL`. Precedence is CLI `--prefix`, `OFFLINE_PREFIX`, the upstream variable, then the default. Configure this before building rather than editing the generated wrapper.
- `runtime`: optional constraints such as `{"libc":"glibc","os_id":"ubuntu","os_version":"26.04"}`. They are checked before installation; musl targets automatically require musl. Without distribution/ABI constraints, only OS/CPU are checked. Describe `--check` accordingly. Implement and test finer constraints, such as a Python ABI, in the adaptation's wrapper.
- `source`: optional local input resolved relative to the recipe, preferred when present. Portable catalog scripts may retain relative `sources/` paths. Omit this field for large resources and download them by URL.
- `scripts`: original text and diffs are saved for every script. Each receives `. "$OFFLINE_ROOT/offline-lib.sh"`. The entrypoint must be listed here. Authored wrappers may omit a URL; identify their purpose in `notes` rather than presenting them as upstream scripts.
- `resources`: paths must start with `resources/`. URLs and aliases must be unique. `offline_fetch URL` writes bytes to stdout; `offline_fetch URL DEST` copies to the destination, with `DEST=-` also writing to stdout. Unknown URLs exit 69 without attempting a download.
- `patches`: applied in order. `old` must be nonempty and occur exactly `count` times; `count` is a positive integer, defaulting to 1. Do not use broad regex replacements to remove unanalyzed logic.
- `env`, `args`, `repeat_args`, `smoke`: support `{bundle}`, `{prefix}`, `{home}`. Each argument is independently quoted; other shell syntax stays literal. For pipelines, explicitly use `sh -ec` or `bash -euo pipefail -c` in smoke tests and ensure earlier failures cannot be hidden by a successful final command. Shell `-c` code must not contain path placeholders; use double-quoted `$OFFLINE_PREFIX`, `$OFFLINE_ROOT`, and `$HOME` so paths are not reparsed as code.
- `HOME`, `OFFLINE_ROOT`, `OFFLINE_AUDIT`: wrapper-managed variables that recipes cannot override. `OFFLINE_PREFIX` is exported automatically. A custom variable such as `INSTALL_ROOT: "{prefix}"` may also supply the prefix to a wrapper.
- `requires`: commands expected on the target and checked before installation, not an automatic dependency-download list. Record libraries, minimum OS versions, and permissions in `notes` and verify them.
- `repeat_args`: passed only during repeat-installation tests, preserving normal first-install behavior and default overwrite protection in tools such as Just.
- `smoke`: at least one executable command. Published adaptations also need a local functional assertion. `|| true` does not establish functional success.

The bundle includes `install.sh`, `repeat.sh`, `smoke.sh`, `offline-lib.sh`, `resources/`, `upstream/`, original sources and diffs under `provenance/`, a manifest, a portable recipe, and SHA256SUMS. Keep verification reports outside the bundle so they do not change the tested inventory. The manifest starts with `not-run`; the external report records the actual verification result.
