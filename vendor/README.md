# Vendored Upstream Sources

This directory contains source snapshots from upstream projects used by `simp`.

- `WeFlow/`: complete WeFlow v5.0.0 source snapshot used to build and run the WeChat/WeLive export tool. Provenance is recorded in `WeFlow/UPSTREAM_SOURCE.md`.
- `simp-skill/`: [BeamusWayne/simp-skill](https://github.com/BeamusWayne/simp-skill), used as the upstream skill reference.
- `goutoujunshi/`: [shengjidaguai-china/goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi), the higher-priority relationship-analysis skill layered on top of `simp-skill`. Provenance is recorded in `goutoujunshi/UPSTREAM_SOURCE.md`.

Nested `.git` directories are intentionally removed so this repository stays a single normal Git project.

Do not store personal WeChat records, exported JSONL files, generated relationship archives, or analysis reports here.

