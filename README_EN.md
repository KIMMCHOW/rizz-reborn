# 重生之我是把妹王

`重生之我是把妹王` is a standalone local project for exporting, parsing, and analyzing WeChat chat records with Codex.

It is not just a copy of `simp-skill`, and it is not a repackaged WeFlow app. It combines upstream export and analysis ideas into one local workspace:

- WeFlow/WeLive-style JSONL exports as the chat-data source;
- `simp-skill` relationship-analysis prompts and memory structure;
- this project's Python CLI for parsing exports, writing reports, and initializing local memory folders;
- Codex running the source code directly against private local folders.

The internal Python package, CLI command, and `/simp` skill command remain named `simp` for compatibility with upstream `simp-skill`, existing tests, and command entry points. The public project display name is `重生之我是把妹王`.

## Upstream References

This project vendors source snapshots from:

- WeChat export GUI/reference: [hicccc77/WeFlow](https://github.com/hicccc77/WeFlow), stored in `vendor/WeFlow/`
- Relationship-analysis skill: [BeamusWayne/simp-skill](https://github.com/BeamusWayne/simp-skill), stored in `vendor/simp-skill/`

The root `SKILL.md`, `prompts/`, `tools/`, and `tests/` are also kept from `simp-skill` as the analysis foundation for this project.

## Graphical Interface

The graphical export workflow is preserved through WeFlow/WeLive.

Use the WeFlow/WeLive GUI to export WeChat records into JSONL files, then let Codex or the Python CLI analyze those exports from source. This project does not replace the WeFlow GUI and should not be packaged as a single `.exe`.

Typical export layout:

```text
record/
  wxid_xxx_123/
    wxid_xxx_123.jsonl
    wxid_xxx_123_media/
  some-group/
    48250421441@chatroom_xxx.jsonl
    48250421441@chatroom_xxx_media/
```

## Features

- Find WeFlow/WeLive JSONL files under an export directory
- Detect group chats vs. 1:1 chats
- Count messages, senders, message types, and reply timing
- Rank candidate interactors in group chats
- Generate Markdown reports
- Initialize `simp-skill` style local memory folders
- Load local private paths and your sender id from `.env`

## Install

```powershell
cd D:\Coding\simp
python -m pip install -e .
```

Source mode without installation:

```powershell
$env:PYTHONPATH = "D:\Coding\simp\src"
python -m simp_project.cli --help
```

## Environment

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Example:

```env
SIMP_ME_WXID=wxid_me
SIMP_CRUSH_ROOT=local_data/crushes
SIMP_WELIVE_RECORD_DIR=local_data/welive-records
SIMP_OUTPUT_DIR=local_outputs
```

`.env` is ignored by git.

## Usage

Put GUI-exported records under:

```text
local_data/welive-records/
```

Inspect an export:

```powershell
python -m simp_project.cli inspect "local_data\welive-records\demo-chat"
```

Write a Markdown report:

```powershell
python -m simp_project.cli report "local_data\welive-records\demo-chat" `
  --name "Demo Target" `
  --output "local_outputs\demo.md"
```

Initialize a local memory folder:

```powershell
python -m simp_project.cli init-crush "local_data\welive-records\demo-chat" `
  --name "Demo Target" `
  --slug "demo"
```

## Privacy

Never commit private chat exports, generated relationship archives, reports, or `.env`.

Ignored private paths include:

- `.env`
- `local_data/`
- `local_outputs/`
- `data/`
- `outputs/`
- `*.jsonl`

Before committing, check:

```powershell
git status --short --ignored
```

## Development

```powershell
python -m pytest -q
```

`pytest.ini` limits collection to the root `tests/` directory so vendored `vendor/simp-skill/tests/` are not collected twice.
