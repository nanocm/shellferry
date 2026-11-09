# Installing Shellferry

Choose one method per host. Every method installs the complete
`skills/shellferry/` directory, including scripts, recipes, evidence, and licenses.
Downloading only `SKILL.md` leaves out files needed to build bundles.

The public repository is [nanocm/shellferry](https://github.com/nanocm/shellferry).
Remote GitHub installation through Skills CLI, Claude's plugin marketplace, and
Codex's built-in installer was verified on 2026-11-09 in isolated directories.
Each installed skill payload was checked against the published source, including
recipes, licenses, and relocated evidence.

| Method | Where to run it | Invocation |
| --- | --- | --- |
| Skills CLI (`npx`) | Terminal | Codex: `$shellferry`; Claude Code: `/shellferry` |
| Claude Code plugin | Claude Code or terminal | `/shellferry:shellferry` |
| Codex built-in installer | Codex conversation | `$shellferry` |
| Local Python installer | Terminal | Codex: `$shellferry`; Claude Code: `/shellferry` |

## Skills CLI (`npx`)

Requires Node.js 22.20+ and access to npm; Git repository sources also require
Git. The [Skills CLI](https://github.com/vercel-labs/skills) discovers the standard
`skills/shellferry/` layout. A separate Shellferry npm package is unnecessary:
npm supplies the installer, and the repository supplies the skill.

Choose your host:

```sh
npx skills add nanocm/shellferry --skill shellferry --agent codex --global
npx skills add nanocm/shellferry --skill shellferry --agent claude-code --global
```

Use `--agent codex claude-code` for both. Omit `--global` for project scope and
run from the intended project. Add `--copy` for independent copies instead of
the default shared directory and links; add `--yes` for noninteractive use.

From a local checkout or extracted release:

```sh
# Run in your target project and supply the source checkout's path.
npx skills add /path/to/shellferry --skill shellferry --agent codex claude-code
```

When already in the source directory, use
`npx skills add . --skill shellferry --agent codex --global`.
Local sources avoid GitHub access; `npx` may still fetch its CLI from npm. Use the
[Python installer](#local-checkout-or-release-archive) for disconnected installation.

Manage Skills CLI installations with the same CLI:

```sh
npx skills list --global
npx skills update shellferry --global
npx skills remove shellferry --agent codex claude-code --global
```

For a local source, install again from its updated directory. Use a GitHub URL
with the release tag to pin a release instead of following the default branch:

```sh
npx skills add https://github.com/nanocm/shellferry/tree/v0.1.0/skills/shellferry --agent codex claude-code --global
```

The `owner/repository@name` shorthand selects a skill name in Skills CLI; it does
not select a Git tag.

## Claude Code plugin

The package includes `.claude-plugin/marketplace.json` and
`.claude-plugin/plugin.json`. The plugin points to the shared `skills/` directory.
Run inside Claude Code:

```text
/plugin marketplace add nanocm/shellferry
/plugin install shellferry@shellferry
```

For a local checkout or extracted release, run in a terminal:

```sh
claude plugin marketplace add /path/to/shellferry
claude plugin install shellferry@shellferry
```

The terminal command also accepts `nanocm/shellferry`. Add
`--scope project` to the install command for project scope. Invoke the plugin
with `/shellferry:shellferry`, then provide the installation command and target.
The standalone skill installed by `npx` or Python uses `/shellferry`.

```sh
claude plugin marketplace update shellferry
claude plugin update shellferry@shellferry
claude plugin uninstall shellferry@shellferry
```

Refresh plugins or start a new session if an installed command does not appear.

## Codex built-in installer

Ask Codex:

```text
$skill-installer install https://github.com/nanocm/shellferry/tree/main/skills/shellferry
```

The URL identifies the complete skill subdirectory. Codex's installer handles
the download and destination. Current discovery includes `~/.agents/skills`;
older installer versions may use `$CODEX_HOME/skills` or `~/.codex/skills`. Check
the path reported by your installed version. Invoke `$shellferry` on the next
turn; restart Codex if discovery does not refresh.

## Local checkout or release archive

From the repository or extracted release:

```sh
python3 install.py --dry-run
python3 install.py
python3 install.py status
```

Windows PowerShell uses `python` instead of `python3`.

The default target is `~/.agents/skills/shellferry`, following the current
[official Codex skill locations](https://developers.openai.com/codex/skills).
Invoke it as `$shellferry`. Codex detects changes automatically; if it does not
appear on the next turn, restart the host.

Some existing Codex installations use `$CODEX_HOME/skills` or `~/.codex/skills`.
Select that layout explicitly:

```sh
python3 install.py --host codex-legacy
```

Do not install the same skill to multiple discovery locations. If you previously
used the prototype named `offline-install`, finish active work with it before
disabling or moving that old skill. The installer does not delete an unrelated
`offline-install` directory.

## Project scope

```sh
python3 install.py --scope project --project-dir /path/to/project
```

This creates `/path/to/project/.agents/skills/shellferry`. Use the same flags for
status, update, and uninstall.

## Other hosts and explicit paths

To install a standalone skill to `~/.claude/skills/shellferry`, run
`python3 install.py --host claude`, then invoke `/shellferry`. A host must have
local execution and file access to run the workflow.

For another skill location:

```sh
python3 install.py --dest /path/to/skills
```

`--dest` names the **parent** skills directory; a `shellferry` child is created.
For example, in PowerShell:

```powershell
python install.py --dest "$env:USERPROFILE\.codex\skills"
```

Manual installation also works: copy `skills/shellferry` into the desired skills
directory. A manual installation is not managed by `install.py`; the installer
refuses to overwrite unmanaged directories.

Use the original manager to update or remove installations made by `npx`,
Claude plugins, or Codex's installer. The Python installer manages only copies
carrying its own receipt. To switch methods, preserve local edits and uninstall
the old copy first.

## Update

Update the checkout with `git pull --ff-only`, or download a newer source/release
archive. From the new version:

```sh
python3 install.py update
```

Updates verify copied file hashes and move the old managed directory to
`.shellferry-backups` next to the skills directory's parent. The backup path is
printed. Backups stay outside skill discovery directories.

If you edited installed files, the update stops. To preserve those edits in a
backup and install the new version:

```sh
python3 install.py update --force
```

`--force` only applies to an installation with a valid Shellferry receipt. It does
not permit overwriting arbitrary directories. For long-term changes, edit the
source checkout and contribute the changes rather than editing an installed copy.

## Uninstall

```sh
python3 install.py uninstall
```

The managed installation is moved to a backup, not permanently deleted. Locally
modified installations require `--force`. Download caches and generated bundles
are not removed.

## Installation verification

Run the real installation commands against an extracted release with temporary
home and project directories:

```sh
python3 tools/package.py
python3 tools/check_installation.py --archive dist/shellferry-0.1.0.zip
```

This requires Node.js 22.20+ and fetches `skills@1.7.6` through `npx`. Claude Code
checks run when its CLI is installed; otherwise the report marks them skipped.
Add `--require-claude` to require that check. The output
`dist/installation-checks.json` includes the tested archive's SHA-256.

Checks cover project and user scope, copy and link installation, both host
destinations, the full skill payload, and evidence matching after relocation.
Claude checks validate both manifests, add the local marketplace, install the
plugin, and inspect its payload. These installation checks do not run an
authenticated agent conversation. The release's separate remote-installation
report covers actual GitHub fetching; local archive checks do not establish it.

## Verification prerequisites

Python 3.10+ is required on the preparation machine. No third-party Python package
is required. For Linux bundle verification, use a working Docker/Podman engine.
The generated installer normally needs no Python on the destination machine.

The simple zoxide example can use the official Ubuntu base image. Other recipes
declare additional prerequisites. Historical validation used extra tools listed
in the [matrix](../skills/shellferry/references/validation-matrix.md); never infer
that the destination has those tools merely because a test image contains them.

For Windows, run preparation in PowerShell and verification inside WSL2. A
Windows path must be translated to the matching `/mnt/...` path before passing it
to a Linux container. `verify.py` is not a native Windows container launcher.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Skill does not appear | Check the selected discovery location; try the next turn or restart the host |
| GitHub access fails | Check connectivity; transfer a complete release archive and use the local Python installer when GitHub is unavailable |
| Claude command name differs | Use `/shellferry` for standalone installation, `/shellferry:shellferry` for the plugin |
| `npx` cannot create links | Add `--copy` |
| Existing directory refused | Use `update` for a managed install; preserve/move a manual installation yourself |
| Python not found | Install Python 3.10+ on the preparation machine; Windows may use `py -3` |
| Container image missing | Pull or build the correct image before testing; test runs use `--pull=never` |
| No matching evidence | Read the mismatch reasons; build and verify the requested version/environment |
| Upstream checksum or patch mismatch | Stop and review the upstream change; do not bypass the check |

The checked-in `plugin.json` follows the portable Agent Plugins layout. It can be
used for plugin packaging; publishing to a plugin directory is a separate step.
