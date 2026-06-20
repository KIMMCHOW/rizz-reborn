# rizz-reborn Project Notes

`rizz-reborn` is a standalone local project for exporting, parsing, and analyzing WeChat chat records with Codex. Its Chinese display name is `重生之我是把妹王`.

It references upstream repositories, but it is not merely a fork of either one. The root README is the user-facing project guide; this file keeps implementation notes.

The Python distribution and main CLI are named `rizz-reborn`; the importable module is `rizz_reborn`. The upstream `/simp` skill command and the `simp` CLI alias remain only for compatibility with `simp-skill`.

## Upstream Sources

This project references and vendors source snapshots from:

- WeChat export tool: [hicccc77/WeFlow](https://github.com/hicccc77/WeFlow), stored at `vendor/WeFlow/`.
- Codex/Claude skill: [BeamusWayne/simp-skill](https://github.com/BeamusWayne/simp-skill), stored at `vendor/simp-skill/`.

Personal analysis archives and generated reports must stay in ignored local folders.

## Quick Start

From `D:\Coding\simp`:

```powershell
python -m pip install -e .
python -m rizz_reborn.cli inspect "local_data\welive-records\some-chat"
python -m rizz_reborn.cli report "local_data\welive-records\some-chat" --name "示例" --output "local_outputs\example.md"
```

Create a new memory folder from an export:

```powershell
python -m rizz_reborn.cli init-crush "local_data\welive-records\some-chat" --name "示例" --slug "example"
```

## Runtime Model

This project is intended to be run from source by Codex or Python scripts. Do not package it as a single `.exe`: Codex should call the source code, read the configured local WeChat export paths, and write private analysis results into ignored local folders.

The graphical export step is preserved through WeFlow/WeLive. Use the GUI to produce JSONL records, then let Codex run the parser and analysis logic from source.

## Local Environment

Local private configuration lives in `.env`, which is ignored by git. Use `.env.example` as the template.

Current environment variables:

- `SIMP_ME_WXID`: your own sender id in WeLive JSONL exports.
- `SIMP_CRUSH_ROOT`: local private relationship-memory folder, defaulting to `local_data/crushes`.
- `SIMP_WELIVE_RECORD_DIR`: local private raw WeLive/WeChat export folder.
- `SIMP_OUTPUT_DIR`: local private generated-report folder.

## Layout

- `SKILL.md`: Codex skill entry.
- `prompts/`: specialist analysis prompts.
- `tools/`: original skill helper tools.
- `src/rizz_reborn/`: project CLI and WeLive JSONL parser.
- `vendor/WeFlow/`: upstream WeFlow repository snapshot.
- `vendor/simp-skill/`: upstream simp-skill repository snapshot.
- `local_data/` or `data/`: optional private memory files, ignored by git.
- `local_outputs/` or `outputs/`: optional generated reports, ignored by git.

## Privacy

Raw WeChat exports, relationship memory files, and generated analysis reports are private. Keep them outside the repository or under ignored local folders such as `data/`, `outputs/`, `local_data/`, and `local_outputs/`.

The private data used during project setup has been migrated locally to:

- `local_data/crushes/`
- `local_data/welive-records/`
- `local_outputs/`

These paths are intentionally ignored by git.
