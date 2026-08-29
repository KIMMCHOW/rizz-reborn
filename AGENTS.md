# Project Agent Rules

These rules extend the user's global agent rules for this repository.

## Local private outputs

- Before generating, moving, or reorganizing any file under `local_outputs/`, read and follow [`docs/agent/LOCAL_OUTPUTS_SOP.md`](docs/agent/LOCAL_OUTPUTS_SOP.md).
- Do not write files directly under `local_outputs/`. Route every artifact by conversation scope, stable subject slug, and analysis domain.
- Keep raw chat exports under `local_data/welive-records/`, relationship memory under `local_data/crushes/`, and generated reports or aggregates under `local_outputs/`.
- Do not use raw WeChat IDs as output directory names. Use stable lowercase ASCII `kebab-case` slugs.
- Private outputs must remain Git-ignored and must never be committed or pushed.
- Before completing an output-producing task, verify that `Get-ChildItem -LiteralPath "local_outputs" -File` returns no files and run `git check-ignore` on representative artifacts.
