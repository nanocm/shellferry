# Installing Shellferry

Choose one method per agent. Every method installs the complete
`skills/shellferry/` directory, including scripts, recipes, evidence, and licenses.
Keep that directory intact; the workflow uses more than `SKILL.md`.

Bundle preparation needs Python 3.10+ and access to the selected downloads or a
populated cache. **Docker and Podman are optional:** they are used only for
installation tests. The destination runs the bundle's shell installer with the
prerequisites declared by its recipe.

| Method | Where to run it | Invocation |
| --- | --- | --- |
| Skills CLI (`npx`) | Terminal | Codex: `$shellferry`; Claude Code: `/shellferry` |
| Claude Code plugin | Claude Code or terminal | `/shellferry:shellferry` |
| Codex built-in installer | Codex conversation | `$shellferry` |
| Local Python installer | Terminal | Codex: `$shellferry`; Claude Code: `/shellferry` |

## Skills CLI (`npx`)

Requires Node.js 22.20+, access to npm, and Git for repository sources. The
[Skills CLI](https://github.com/vercel-labs/skills) installs Shellferry from this
repository's `skills/shellferry/` directory.

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
npx skills add https://github.com/nanocm/shellferry/tree/v0.1.1/skills/shellferry --agent codex claude-code --global
```

The `owner/repository@name` shorthand selects a skill name in Skills CLI; it does
not select a Git tag.

## Claude Code plugin

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

Keep one active installation per agent. If you used the prototype named
`offline-install`, finish its active tasks before disabling it. This installer
leaves the prototype directory in place.

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

For manual installation, copy the complete `skills/shellferry` directory into
the chosen skills directory. Update that copy manually; `install.py` manages only
copies carrying its own receipt.

Use the original manager to update or remove installations made by `npx`,
Claude plugins, or Codex's installer. To switch methods, preserve local edits
and uninstall the old copy first.

## Update

Update the checkout with `git pull --ff-only`, or download a newer source/release
archive. From the new version:

```sh
python3 install.py update
```

Updates check copied file hashes and move the previous managed installation to
`.shellferry-backups`, outside skill discovery directories. The command prints
the backup path.

If you edited installed files, the update stops. To preserve those edits in a
backup and install the new version:

```sh
python3 install.py update --force
```

`--force` requires a valid Shellferry receipt. Keep ongoing customizations in a
source checkout so they can be reviewed and carried into later versions.

## Uninstall

```sh
python3 install.py uninstall
```

The command moves the managed installation to a backup. Locally modified
installations require `--force`; download caches and generated bundles stay in
place.

## Installation verification

Maintainers can test the skill's installation channels against an extracted
release, using temporary home and project directories:

```sh
python3 tools/package.py
python3 tools/check_installation.py --archive dist/shellferry-0.1.1.zip
```

This requires Node.js 22.20+ and fetches `skills@1.7.6` through `npx`. Claude Code
checks run when its CLI is installed; otherwise the report marks them skipped.
Add `--require-claude` to require that check. The output
`dist/installation-checks.json` includes the tested archive's SHA-256.

Checks cover project and user scope, copy and link installation, both host
destinations, the full skill payload, and evidence matching after relocation.
Claude checks validate both manifests, add the local marketplace, install the
plugin, and inspect its payload. This suite covers installation and file
discovery; authenticated agent conversations need a separate test.

Remote GitHub installation through Skills CLI, Claude's marketplace, and Codex's
built-in installer was tested on 2026-11-09 in isolated directories. The complete
installed payloads were compared with the published source, and evidence was
queried after relocation. The [v0.1.0 release](https://github.com/nanocm/shellferry/releases/tag/v0.1.0)
includes the remote-installation report.

## Verification prerequisites

Offline installation testing is optional. Shellferry builds and packages by
default. To request a test, add “verify the final archive with Podman and
networking disabled” to your prompt, or run `verify.py` as shown in the
[README](../README.md#build-and-optionally-verify).

The automated Linux verifier requires a working Docker or Podman engine and a
prepared matching image. Without a test, the bundle is delivered as **built,
installation not tested** (`not-run`). Source hashes, resource hashes, and exact
patch matches are checked during every build. If a requested test cannot start,
the agent reports the cause and the remaining verification work.

The simple zoxide example can use the official Ubuntu base image. Other recipes
declare additional prerequisites. Prepared images include the tools listed in
the [matrix](../skills/shellferry/references/validation-matrix.md); the destination
must provide those tools unless the bundle includes them.

On Windows, native Python can prepare bundles. Run optional Linux verification
inside WSL2 and translate paths to their actual `/mnt/...` locations before
passing them to the container.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Skill does not appear | Check the selected discovery location; try the next turn or restart the host |
| GitHub access fails | Check connectivity; transfer a complete release archive and use the local Python installer when GitHub is unavailable |
| Claude command name differs | Use `/shellferry` for standalone installation, `/shellferry:shellferry` for the plugin |
| `npx` cannot create links | Add `--copy` |
| Existing directory refused | Use `update` for a managed install; preserve/move a manual installation yourself |
| Python not found | Install Python 3.10+ on the preparation machine; Windows may use `py -3` |
| Container image missing | For a requested test, pull or build the matching image first; tests use `--pull=never`. Build-only work needs no image |
| No matching evidence | Review the mismatched inputs before building; run a fresh test if requested or needed for catalog publication |
| Upstream checksum or patch mismatch | Stop and review the upstream change; do not bypass the check |
