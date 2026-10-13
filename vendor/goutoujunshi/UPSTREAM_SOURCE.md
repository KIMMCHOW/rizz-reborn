# goutoujunshi upstream source provenance

This directory vendors a complete snapshot of the `goutoujunshi` skill so the repository pins the exact revision it layers on top of `simp`.

- Project: `shengjidaguai-china/goutoujunshi` (狗头军师 · Goutoujunshi)
- Commit: `6db7354a4002dc7c448a9c87ffdad8132570c9d3`
- Commit date: `2026-09-15T13:49:39+08:00`
- Retrieved on: `2026-10-14`
- Retrieval method: shallow clone of `https://github.com/shengjidaguai-china/goutoujunshi.git`, then copy of every tracked path except the nested `.git` directory
- Integrity check: 68 tracked files copied; nested `.git` directories: 0; the same content matched the locally installed skill at `C:\Users\zhouz\.codex\skills\goutoujunshi` byte-for-byte after normalizing line endings

## Verification

The upstream validator was run against this snapshot on `2026-10-14`:

```powershell
python vendor\goutoujunshi\scripts\validate_skill.py
python vendor\goutoujunshi\scripts\validate_skill.py --runtime
```

Both runs printed `goutoujunshi validation passed`. `tests\test_vendored_goutoujunshi_snapshot.py` keeps this check running with the rest of the suite.

## License

The upstream project is MIT licensed. `LICENSE` and `LICENSE.zh-CN.md` are retained unchanged in this directory.

## Notes for maintainers

- Treat this directory as a read-only upstream reference. Do not edit files here to change project behavior; project-level routing and priority rules live in `docs/agent/SKILL_INTEGRATION.md` and the repository root `SKILL.md`.
- `SKILL.md` in this snapshot is intentionally outside the project's editable analysis rules. The upstream validator enforces its own line, character, and token budget, so keep it unmodified.
- The upstream `README.md` badges still point at `powerycy/goutoujunshi`; the snapshot source of record for this repository is `shengjidaguai-china/goutoujunshi` at the commit above.
- `scripts/memory_store.py` only writes a bounded SQLite file under the operating system user data directory, and only after explicit user consent. It never writes into this repository. Keep it that way: no personal chat content, archives, or generated reports belong in `vendor/`.
