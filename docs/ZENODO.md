# Archiving releases with Zenodo

1. Sign in at https://zenodo.org with GitHub and open **GitHub** under your account settings.
2. Flip the switch next to this repository.
3. Create a GitHub release (for example `v2026.10` after a Mathlib bump or a batch of new statements).
4. Zenodo archives the release tarball and mints a DOI; the first release also gets a *concept DOI* that always resolves to the latest version.
5. Put the concept DOI badge in the README once it exists.

Optional: add a `.zenodo.json` at the repository root with `creators`, `title`, `description`, `license` (`Apache-2.0` for code; note the CC-BY-4.0 content licence in the description) so the deposit metadata is filled in automatically.
