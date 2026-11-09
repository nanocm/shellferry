# Shellferry

把在线安装脚本转换成可搬运的离线安装包。

[English](README.md) · [安装指南](docs/installation.md) · [已验证软件](skills/shellferry/references/validation-matrix.md) · [参与贡献](CONTRIBUTING.md)

[![Checks](https://github.com/nanocm/shellferry/actions/workflows/ci.yml/badge.svg)](https://github.com/nanocm/shellferry/actions/workflows/ci.yml)

一条 `curl | sh` 命令背后，可能还有脚本下载、版本查询、二进制获取和运行时安装。远程机器访问 GitHub 不稳定时，任何一步都可能中断。Shellferry 在联网机器上收集这些资源，把安装器的下载步骤改为读取包内文件，再将整个安装包搬到目标机器。

给它安装命令和目标环境即可：

```text
命令：curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
目标：Ubuntu 22.04，x86_64，普通用户
输出：zoxide.tar.gz、SHA-256、本地安装脚本、安装说明
```

Shellferry 是供 Codex 和 Claude Code 使用的 skill，配有负责下载、精确补丁、校验和打包的 Python 程序。目前包含 **105 个软件的 106 份固定配方**，均有离线安装测试记录。适配新安装器时，代理需要能读写本地文件并执行命令。

**打包不需要 Docker 或 Podman。** 默认构建和打包，安装验证按需执行。准备机器需要 Python 3.10+，并能获取所选资源；请求断网安装测试后，会取得与最终压缩包对应的容器测试报告。目标机器直接运行包内安装器。

## 安装

为每个代理选择一种安装方式。

### 通过 npx

需要 Node.js 22.20+：

```sh
# Codex
npx skills add nanocm/shellferry --skill shellferry --agent codex --global

# Claude Code
npx skills add nanocm/shellferry --skill shellferry --agent claude-code --global
```

使用 `--agent codex claude-code` 可同时安装到两者；去掉 `--global` 则安装到当前项目。固定版本、更新和卸载见[安装指南](docs/installation.md#skills-cli-npx)。

### Claude Code 插件

在 Claude Code 内运行：

```text
/plugin marketplace add nanocm/shellferry
/plugin install shellferry@shellferry
```

插件使用 `/shellferry:shellferry` 调用。通过 npx 安装的独立技能使用 `/shellferry`。

### Codex 内置安装器

对 Codex 说：

```text
$skill-installer install https://github.com/nanocm/shellferry/tree/main/skills/shellferry
```

安装后使用 `$shellferry` 调用。

### 本地或离线安装

下载并解压[发布包](https://github.com/nanocm/shellferry/releases)，在解压目录运行：

```sh
python3 install.py                 # Codex
python3 install.py --host claude   # Claude Code
```

Windows 使用 `python`。这种方式只需要 Python 3.10+ 和完整发布包。[更多安装选项](docs/installation.md#local-checkout-or-release-archive)。

## 使用

在 Codex 中：

```text
使用 $shellferry，将下面的命令转换成离线安装包。
目标：Ubuntu 22.04，x86_64，普通用户。
收集各安装阶段所需资源。只打包，跳过安装测试。

curl -fsSL https://bun.sh/install | bash
```

需要本次验证时，将最后一句改为“同时用 Podman 在断网环境中验证最终压缩包”。在 Claude Code 中，根据安装方式使用 `/shellferry` 或 `/shellferry:shellferry`。回复和安装说明跟随你的语言。

Shellferry 保留上游安装脚本，将下载步骤的修改记录为精确补丁。资源 URL 和摘要都会固定，后续安装阶段也纳入分析，目标环境的前置依赖会写进交付说明。已有配方可以复用这些分析；新安装器则根据指定环境审阅和适配。

## 构建与可选验证

已有配方也能直接从命令行构建。以下命令生成 zoxide 安装包，全程不需要容器：

```sh
python3 skills/shellferry/scripts/catalog.py list
python3 skills/shellferry/scripts/catalog.py show zoxide
python3 skills/shellferry/scripts/catalog.py build zoxide --output work/zoxide
python3 skills/shellferry/scripts/convert.py archive work/zoxide --output dist/zoxide.tar.gz
```

此时压缩包和 `.sha256` 文件已可传输。没有执行安装测试时，结果应标明 **已构建，未执行安装验证**（`not-run`）。资源摘要和补丁匹配检查在每次构建时都会执行。

如果需要在 Ubuntu 22.04 上测试这个包，再运行：

```sh
# 可选。镜像准备可以联网，实际安装测试禁用网络。
podman pull docker.io/library/ubuntu:22.04
python3 skills/shellferry/scripts/verify.py dist/zoxide.tar.gz \
  --engine podman --image docker.io/library/ubuntu:22.04 \
  --output dist/zoxide.validation.json
```

测试会重新解压最终归档，以普通用户和干净 HOME 安装，运行本地功能，再重复安装。它还会检查含空格路径，并捕获常见下载命令。成功报告记录被测压缩包的摘要和实际环境。

Windows 可以用本机 Python 下载和打包；可选的 Linux 测试在 WSL 中执行，文件路径需换成对应的 Linux 路径。使用 Docker 时，将命令替换为 `docker pull` 和 `--engine docker`。

## 在目标机器安装

传入压缩包和校验文件。以 zoxide 为例：

```sh
sha256sum -c zoxide.tar.gz.sha256
tar -xzf zoxide.tar.gz
sh zoxide/install.sh --check
sh zoxide/install.sh
export PATH="$HOME/.local/bin:$PATH"
eval "$(zoxide init bash)"
```

目标机器需要满足配方声明的命令和运行库要求。例如，`bun-ubuntu22` 携带私有 unzip 工具及其依赖库，`bun` 则要求系统已安装 unzip。生成的 shell 包装器无需代理、Python 或容器引擎；具体软件仍可能依赖 Python 或其他运行时。

## 已验证软件

已有适配包括 Bun、Deno 等运行时，zoxide、fzf、Starship 等 Shell 工具，uv、Poetry、pnpm 等包工具，以及 .NET SDK、SDKMAN! + JDK、code-server、Pulumi 等开发工具。

**105 个不同软件**均有 Linux x86_64 离线安装测试记录。106 份配方包含 101 份 Shell 安装器适配、3 份源码安装器适配和 2 份 Python 安装器适配。Bun 有两种环境配方，按一个软件计数。每份当前配方都有与其输入、构建器和验证器相匹配的证据。

[验证矩阵](skills/shellferry/references/validation-matrix.md)列出了全部版本、环境、功能检查和报告。测试使用 Ubuntu 22.04 或 26.04。管理器、云工具和项目依赖的测试范围各有不同，选择配方时可查阅[验证范围与前置条件](skills/shellferry/references/known-limitations.md)。

查询已有证据无需下载或启动容器：

```sh
python3 skills/shellferry/scripts/catalog.py evidence zoxide \
  --os-id ubuntu --os-version 22.04
```

匹配后可以复用既有转换判断，新生成的压缩包仍单独记录本次测试状态。配方和报告随仓库提供，下载缓存只是可选加速。详见[证据匹配机制](skills/shellferry/references/shared-evidence.md)。

## 开发与许可

可安装的技能位于 `skills/shellferry/`，其中的脚本负责转换、打包和验证，`assets/catalog/` 保存配方与安装器快照。仓库检查命令：

```sh
python3 tools/check_repo.py
python3 tools/run_tests.py
python3 tools/coverage.py --check --minimum 105
python3 tools/package.py
```

添加配方见 [CONTRIBUTING.md](CONTRIBUTING.md)，测试代理安装渠道见[安装验证](docs/installation.md#installation-verification)。

Shellferry 自己的代码与文档使用 [MIT](LICENSE)。上游脚本和片段保留各自许可，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。仓库提供配方和证据，软件二进制在构建时下载；重新分发生成的安装包前，需要核对其中资源的上游许可。
