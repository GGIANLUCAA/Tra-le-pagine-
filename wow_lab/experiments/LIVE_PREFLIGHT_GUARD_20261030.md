# WOW LAB — mandatory live preflight, 2026-10-30

Scope: `wow_lab/` on `experiment/wow-lab-release-queue-hardening-20261030` only.

## Concrete safety change

- `engine.run()` now refuses to start unless `GITHUB_REPOSITORY` is exactly `GGIANLUCAA/Tra-le-pagine-`, `GITHUB_RUN_ID` is numeric, and `GITHUB_TOKEN` is present.
- This closes the former offline bypass: `recent_history()` and `ensure_no_parallel_wow_render()` intentionally return empty/no-op outside the GitHub runner for isolated unit tests. Without an entrypoint guard, a local render could accidentally proceed without checking real releases and active runs.
- `engine.run()` refuses to reuse a populated run directory and does not create an output folder until the GitHub queue, release history, and current UTC slot have all passed their live checks.
- Eight new regression tests cover invalid contexts, missing credentials, existing artifacts, and preflight ordering.

## Validation and blockers

- GitHub compare confirms all changes against `main` are confined to `wow_lab/`. No core workflow, site, Vidu, or other project files changed.
- New tests are committed but **not executed in GitHub Actions** on this experimental branch. The workflow's push trigger only includes its original experiment branch; changing that trigger would be outside the authorized `wow_lab/` scope.
- The connector currently provides file and known-run reads, but not exhaustive live release/run listing. Public GitHub API fetches from the available web/container environment failed. Thus **the current release slot and queue have not been independently verified in this execution**.
- No real CC0 source image, actual subject mask, FFmpeg output, cover, ZIP or artistic QA was produced during this run. Do not create or publish a release from these code changes.
- Remaining race: the live queue check is not an atomic lock against independent WOW LAB workflows. A GitHub-wide concurrency group or equivalent server-side reservation would require a reviewed workflow change outside this branch's authorized path.

Decision: **skip production**, fail closed rather than risk duplicate release or misleading quality claim.
