# Shellferry

**把在线安装脚本转换成可搬运、经过验证的离线安装包。**

[English](README.md) · [安装指南](docs/installation.md) · [验证矩阵](skills/shellferry/references/validation-matrix.md) · [参与贡献](CONTRIBUTING.md)

[![Checks](https://github.com/nanocm/shellferry/actions/workflows/ci.yml/badge.svg)](https://github.com/nanocm/shellferry/actions/workflows/ci.yml)

给 Shellferry 一条安装命令和目标机器信息，它会收集安装阶段所需的脚本、二进制和依赖，生成可搬运的安装包，用于访问 GitHub 不稳定或完全无法联网的服务器。

```text
输入：curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
目标：Ubuntu 22.04 · x86_64 · 普通用户
输出：zoxide.tar.gz + SHA-256 + 安装说明 + 验证报告
验证：Podman/Docker --network none
```

这是一个**带 Python 辅助程序的 agent skill**，包含覆盖 105 个软件的 106 份固定配方。代理处理新软件的安装逻辑；程序负责精确补丁、摘要校验、打包和测试。已有适配也可直接通过命令行构建。

Skill 指令和技术参考统一使用英文维护；回复与生成的安装说明跟随用户语言，中文请求仍使用中文。

## 安装

选择一种安装方式即可。可以直接从 GitHub 安装，也可以下载[发布包](https://github.com/nanocm/shellferry/releases)进行[本地安装](docs/installation.md#local-checkout-or-release-archive)。

### 通过 npx 安装到 Codex 或 Claude Code

需要 Node.js 22.20+，选择所用的代理：

```sh
# Codex
npx skills add nanocm/shellferry --skill shellferry --agent codex --global

# Claude Code
npx skills add nanocm/shellferry --skill shellferry --agent claude-code --global
```

去掉 `--global` 即安装到当前项目；同时安装到两者可用 `--agent codex claude-code`。[本地目录安装、更新和卸载](docs/installation.md#skills-cli-npx)也由同一 CLI 完成。

### Claude Code 插件

在 Claude Code 内执行：

```text
/plugin marketplace add nanocm/shellferry
/plugin install shellferry@shellferry
```

插件调用方式为 `/shellferry:shellferry`。通过 `npx` 安装独立 skill 时，调用方式为 `/shellferry`。

### Codex 内置安装器

对 Codex 说：

```text
$skill-installer install https://github.com/nanocm/shellferry/tree/main/skills/shellferry
```

安装后用 `$shellferry` 调用。安装位置由当前 Codex 的安装器决定，现行与旧版目录见[安装指南](docs/installation.md#codex-built-in-installer)。

### 本地仓库或离线发布包

在仓库或发布包解压目录执行，选择所用的代理：

```sh
# Codex
python3 install.py

# Claude Code
python3 install.py --host claude
```

Windows PowerShell 将 `python3` 换为 `python`。此方式只需 Python 3.10+ 和完整发布包，可离线安装，并提供更新与备份管理。完整选项见[安装指南](docs/installation.md)。

## 使用

在 Codex 中：

```text
使用 $shellferry，将下面的命令转换成离线安装包。
目标：Ubuntu 22.04，x86_64，普通用户。
收集各安装阶段所需资源，并用 Podman 断网验证。

curl -fsSL https://bun.sh/install | bash
```

输出包括安装包、SHA-256、本地安装脚本和与成品绑定的验证报告。把包传到目标机器，按生成的说明安装。

在 Claude Code 中，将同一请求开头改为 `/shellferry`（独立 skill）或 `/shellferry:shellferry`（插件）。生成安装包需要 Python 和本地执行能力；断网验证还需 Podman 或 Docker。

## 核心能力

- **追踪安装阶段**：版本查询、架构选择、二阶段脚本、二进制引导器、主题、补全等都纳入分析。
- **保留可审阅差异**：保存原脚本与精确补丁；上游内容变化或匹配次数不符时要求重新分析。
- **固定资源**：记录 URL 和摘要，明确区分上游提供的校验值与本地计算的固定值。
- **验证真实成品**：从压缩包解压到新位置，以普通用户在 `--network none` 容器中安装，检查本地功能和重复安装。
- **共享分析和验证经验**：配方、依赖清单、环境、失败修复与证据随仓库交付，其他用户无需作者的下载缓存。

遇到新安装器时，代理会追踪系统包、源码编译和后续下载程序，再为指定目标编写配方并验证。

## 环境要求

| 位置 | 要求 |
| --- | --- |
| 准备机器 | Python 3.10+，可获取上游资源；新适配需要具有本地文件和命令执行能力的代理 |
| 验证机器 | 可用的 Linux Podman/Docker 和匹配镜像；Windows 可通过 WSL2 使用 |
| 目标机器 | 对应配方声明的基础命令及运行库；生成的包装器不要求安装代理或 Python |

例如，`bun-ubuntu22` 携带私有解压工具；普通 `bun` 配方则要求目标已有 `unzip`。选择前查看依赖说明。

## 直接构建已有适配

以下示例构建 zoxide，并在 Ubuntu 22.04 中验证：

```sh
python3 skills/shellferry/scripts/catalog.py list
python3 skills/shellferry/scripts/catalog.py show zoxide
python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide
python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz

# 准备镜像时允许联网；下面的实际安装测试禁用网络。
podman pull docker.io/library/ubuntu:22.04
python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \
  --engine podman --image docker.io/library/ubuntu:22.04 \
  --output dist/zoxide.validation.json
```

Windows 可用本机 Python 构建，在 WSL 中使用对应 Linux 路径执行验证。Docker 使用 `docker pull` 与 `--engine docker`。

目标机器上的安装命令：

```sh
sha256sum -c zoxide.tar.gz.sha256
tar -xzf zoxide.tar.gz
sh zoxide/install.sh --check
sh zoxide/install.sh
export PATH="$HOME/.local/bin:$PATH"
eval "$(zoxide init bash)"
```

## 已验证范围

**105 个不同软件已通过 Linux x86_64 离线安装验证。** 当前 106 份配方都有与配方、资源固定值、构建器和验证器相匹配的证据。测试覆盖最终归档、普通用户安装、含空格路径、本地功能和重复安装；Bun 的额外环境配方仍只计一个软件。

| 类别 | 软件 |
| --- | --- |
| 运行时与包工具 | Bun、Deno、pnpm、Yarn + Node.js、nvm + Node.js、rustup + Rust |
| Python 与环境 | uv、Ruff、Pixi、Poetry、PDM、Micromamba |
| Shell 与终端 | Starship、Atuin、zoxide、fzf、skim、Oh My Zsh、Bash-it、Bats |
| 开发与数据 | just、Go Task、xmake、cargo-dist、cargo-auditable、Dolt、rqlite |
| 云与运维 | Helm、Flux、OpenTofu、k3d、Istio CLI、Porter、Trivy、Syft |
| 版本管理器 | fnm、mise、Volta、pyenv、rbenv、GHCup、opam、Perlbrew |
| SDK、编辑器与云 CLI | SDKMAN! + Temurin JDK、.NET SDK、code-server、Pulumi + random 插件、Google Cloud CLI + 随包 Python |

上表是部分示例，全部版本、功能检查、环境和报告见[完整验证矩阵](skills/shellferry/references/validation-matrix.md)。106 份配方包括 **101 份 Shell 安装器、3 份源码安装器、2 份 Python 安装器适配**。新增测试主要使用 Ubuntu 22.04，部分原有配方使用 Ubuntu 26.04。[已知限制](skills/shellferry/references/known-limitations.md)记录了前置条件和未通过项，例如 Miniforge 官方安装器拒绝含空格路径。

管理器本体安装不等于其未来需要的所有运行时和项目依赖都已收集。fnm、mise 的现有检查覆盖管理器功能；npm、Python、Cargo、Conda 项目依赖需单独准备。ARM64、macOS、Alpine、完整 systemd 服务和内核模块不在上述已发布验证范围中。

## 用共享证据加速

```sh
python3 skills/shellferry/scripts/catalog.py evidence zoxide \
  --os-id ubuntu --os-version 22.04
```

匹配会检查配方、脚本固定值、系统、构建器和验证器。匹配后可以直接复用既有转换判断，但不能把旧报告当成新生成安装包已经运行的证明。用户要求本次断网验证时仍运行一次。

下载缓存只是可选加速；新用户可以从官方固定 URL 构建。仓库携带小型配方和证据，不携带作者的二进制缓存或本地镜像。[证据机制](skills/shellferry/references/shared-evidence.md)说明了适用条件。

## 开发与许可

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
python3 tools/package.py
```

单元测试不联网；Linux 执行 shell 回归，其他平台跳过对应检查。GitHub Actions 提供手动触发的实际下载与 Docker 断网测试。贡献新适配见 [CONTRIBUTING.md](CONTRIBUTING.md)。

安装兼容检查调用真实 Skills CLI 和本机可用的 Claude Code，将解压后的发布包安装到隔离目录，逐文件校验完整性，并核对迁移后的证据。复现方式见[安装验证](docs/installation.md#installation-verification)。

根目录的 `plugin.json` 提供可携带插件元数据，不代表已上架插件目录。此技能需要本地执行能力，纯聊天宿主无法运行打包和容器测试。

本项目自己的代码与文档使用 [MIT](LICENSE)。保存的上游脚本及片段保留各自许可，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。下载的软件继续遵循上游许可。

部分独立安装器仓库尚未确认完整脚本的再分发许可，其完整原文在构建时获取，不包含于本项目源码发布包；具体名单见[来源与许可说明](skills/shellferry/THIRD_PARTY_NOTICES.md)。公开分发生成的安装包前，需核对其中资源的再分发条件。
