# Maintainer and user manifests

The attached Release’s `MANIFEST.json` lists maintainer source files as well as user material. It is not an instruction to copy the whole repo into an owner workspace.

For setup and updates, run staged `.claude/cowork/workspace.py plan "<Release>"`. Its projected manifest lists only user workspace files, their source inside staging, normalized `sha256` and mode. Cowork-specific instructions and clean memory rules/index replace maintainer variants; the memory layout comes from the personal-memory project scaffold. Fresh creation writes that projected manifest without staging-only `source` fields into the workspace.

`START-HERE.md` and the shipped Cowork environment preference are reference-only and excluded, along with their generated rule/index pointers. Existing owner versions are preserved, never automatically deleted.

The user manifest excludes maintainer `.claude/skills/`, persona libraries, tests, setup/build scripts and `.skill` archives. Packages remain in staging for Cowork Save skill cards; `.claude/cowork/skills/index.json` is retained for future comparisons. A projected file must never overwrite owner content merely because it appears in a manifest.

- `merge`: shared user files, replaced only under the approved update plan.
- `seed` and `local`: starter material owned by the user; preserve and reconcile it rather than resetting it.
- `sha256`: text hashes normalize CRLF to LF. Line-ending-only differences are not personal modifications; compare binary files without rewriting their bytes.
- `mode`: expected file mode where the filesystem supports it.

For old workspaces, their installed manifest helps identify shipped versus owner content. It may include old skill sources; that does not make those sources part of the new user-file plan or authorize deletion. Preserve custom skills, edited files and unknown paths, and ask about real conflicts. Keep the verified full backup and owner recovery protocols even when hashes match. The experimental helper in `UPDATE-RECOVERY.md` adds exact raw-byte operation hashes and retained recovery; projected manifest membership alone still grants no replacement permission.
