SDKMAN installer and Java hook snapshots are Apache-2.0 work from
`sdkman/sdkman-hooks`. The bootstrap retains its original copyright notice:
Copyright 2017 Marco Vermeulen. Both files are preserved byte for byte;
the recipe records the conversion patches separately. Generated endpoint
hashes and the reviewed template commit are recorded in `PROVENANCE.json`.
The recipe also repairs the original initialization snippet's path quoting:
Bash `printf %q` serializes the selected prefix, literal variable references
load the initialization file, and `printf` writes the snippet without
interpreting backslashes. The original profile selection and append guards
remain in place; the source snapshots are unchanged.

`sources/offline-wrapper.sh` and `sources/offline-transport.sh` are original
Shellferry work under the repository's MIT license. The wrapper uses the
official bootstrap, SDKMAN installation functions, native components and
Java post-install hook. The local transport exists only in the installation
process and accepts the one bundled Java version. Its `java` candidate list
and exact-version validation decision are minimal authored offline selection
data. The full dynamic API responses are neither vendored nor required when
building a new bundle.

SDKMAN CLI 5.24.0 and native CLI 0.8.0 are Apache-2.0. Eclipse Temurin JDK
21.0.13+9 declares GPL version 2 with the Classpath Exception; its archive
also contains the OpenJDK Assembly Exception and third-party notices.
These release artifacts are downloaded during bundle construction. Their
original license and notice files remain in the archive and installed JDK.
The source repository contains recipes and evidence, not the JDK binary.

The skill's `third-party.json` inventory contains file hashes and source
locations for the accompanying `sdkman-*` license texts in `LICENSES/`.
