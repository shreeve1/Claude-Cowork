# Coding standards

These standards cover workspace scripts and configuration.

- Make the smallest change that solves the requested problem; preserve owner data and existing interfaces.
- Use Python's standard library when sufficient. Declare additional dependencies where needed.
- Resolve paths explicitly; support spaces, Unicode and Windows path conventions. Keep file operations inside the intended target and check resolved paths before recursive deletion or moving.
- Use subprocess argument lists rather than shell-built commands. Check exit codes and report actionable failures without credentials.
- Keep scripts import-safe. Separate reusable logic from command-line entry points.
- Make resumable operations safe to retry; preserve backups and conflict handling.
- Run relevant existing tests. Add tests for meaningful behavior changes, especially merge, rollback, path safety and owner-data preservation.
- Before committing a skill-script change, a `reviewer` agent reviews the diff against this file. Fix actionable findings.
- Keep commits concise, at most 72 characters in the subject. Run checks directly when hooks are disabled; never bypass an enabled hook.
