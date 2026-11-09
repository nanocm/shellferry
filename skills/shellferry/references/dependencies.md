# Collect offline dependencies

Distinguish the application, managed runtimes, installer prerequisites, shared libraries, and project dependencies. Set the scope from the user's goal and explain how to supply any missing components.

## Prebuilt binaries and runtime libraries

Choose the release for the target OS/CPU/libc, inspect ELF/Mach-O metadata and minimum library versions, and run it in a clean container. For missing libraries such as `libatomic.so.1`, collect dependencies from the matching distribution's official packages. Use offline system packages or a private library directory; avoid setting `LD_LIBRARY_PATH` globally.

The tested nvm + Node 26 adaptation carries Ubuntu 26.04's libatomic1 deb, extracts it with `dpkg-deb`, and sets the library path only in its Node launcher. Its compatibility is specific to that target. Compiling Rust metadata exercises the compiler frontend; building executables additionally requires a matching linker and system headers, followed by execution of the result.

## System packages

- Debian/Ubuntu: match the target distribution, architecture, repositories, and installed state. Consider apt-offline or resolve the full Depends/Pre-Depends closure in a matching clean container. Collect debs and checksums and create a local repository/source. Downloading one package or copying an existing cache is usually incomplete.
- RHEL/Fedora: collect RPM dependencies for the target releasever/architecture, including module streams. Explicitly disable remote repositories during offline installation.
- Alpine: match the release and architecture, collect APK dependencies and signatures, and install from a local repository/cache.

Package installation and service startup may need root. Test inside containers or authorized targets; do not change the preparation host's system merely to build a bundle. Use a matching VM or machine for systemd/kernel behavior that containers cannot establish.

## Python, Node, and Rust project dependencies

- Python: pin the Python ABI/platform and lockfile, prepare a wheelhouse with transitive dependencies, and use `--no-index --find-links`. Include build dependencies for wheels built from source. The uv executable does not supply a Python interpreter or project wheels.
- npm/pnpm/Bun: pin the lockfile and runtime, prepare an offline store/tarballs, and inspect optional platform dependencies and postinstall downloads such as browsers or native addons. Test the actual project installation and a local function before claiming offline project support.
- Rust: prepare the complete minimal toolchain distribution tree from the channel manifest. Cargo projects need vendored dependencies, a lockfile, and local source configuration. Collect system build dependencies separately.

## Git and source builds

Pin the commit and collect recursive submodules and LFS objects. Use a git bundle or complete source archive, checking whether build or runtime behavior needs `.git` metadata. Prepare matching toolchains and system dependencies, then build and run in the disconnected environment.

## Missing prerequisite commands

Check whether the target already provides tools such as unzip, openssl, and xz. If not, collect compatible offline system packages or standalone tools and encode their setup order in the local wrapper. Do not leave `apt update` or online prerequisite installation as a fallback. Tools added while preparing the test image define that test baseline and must be disclosed in the delivery.
