from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from .wechat_export import find_jsonl, load_messages, render_markdown_report, summarize

CN_TZ = timezone(timedelta(hours=8))


def _load_dotenv() -> None:
    """Load simple KEY=VALUE pairs from .env without adding a runtime dependency."""
    candidates = [Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_dotenv()
DEFAULT_ME = os.environ.get("SIMP_ME_WXID", "wxid_me")
DEFAULT_CRUSH_ROOT = os.environ.get("SIMP_CRUSH_ROOT", "local_data/crushes")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def cmd_inspect(args: argparse.Namespace) -> int:
    export = find_jsonl(args.path)
    messages = load_messages(export)
    summary = summarize(messages, args.me, args.limit)
    print(json.dumps({"source": str(export), **summary}, ensure_ascii=False, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    export = find_jsonl(args.path)
    messages = load_messages(export)
    summary = summarize(messages, args.me, args.limit)
    report = render_markdown_report(args.name, export, summary)
    out = Path(args.output)
    _write_text(out, report)
    print(str(out))
    return 0


def cmd_init_crush(args: argparse.Namespace) -> int:
    export = find_jsonl(args.path)
    messages = load_messages(export)
    summary = summarize(messages, args.me, args.limit)
    now = datetime.now(CN_TZ).replace(microsecond=0).isoformat()
    root = Path(args.root)
    crush_dir = root / args.slug
    (crush_dir / "memories" / "chats").mkdir(parents=True, exist_ok=True)

    stage = "identity_mapping" if summary["is_group"] else "breaking_ice"
    score = 20 if summary["is_group"] else 35
    profile = f"""---
name: "{args.name}"
slug: "{args.slug}"
created_at: "{now}"
updated_at: "{now}"
mode: "hybrid"
---

# {args.name}

## 基本信息

- 昵称/称呼：{args.name}
- 关系：{"群聊导出对象，暂未锁定单一联系人" if summary["is_group"] else "微信私聊对象"}
- 当前阶段：{stage}
- 数据来源：`{export}`
- 时间范围：{summary["range_start"]} 到 {summary["range_end"]}

## 最近互动摘要

- 总消息：{summary["total_messages"]}
- 我的消息：{summary["my_messages"]}
- 活跃发言人：{summary["active_senders"]}
"""
    if summary["is_group"]:
        profile += "\n## 候选互动对象\n\n"
        for idx, row in enumerate(summary.get("candidates", []), start=1):
            profile += (
                f"{idx}. `{row['sender']}`：总 {row['messages']} 条；"
                f"相邻互动 {row['adjacent_interactions']} 次。\n"
            )

    state = f"""---
slug: "{args.slug}"
updated_at: "{now}"
stage: "{stage}"
mode: "hybrid"
score: {score}
---

# 当前状态

## 阶段判断

{"当前是群聊画像建档，先确认目标身份，再分析单人信号。" if summary["is_group"] else "当前是私聊导出建档，可继续分析主动性、回复速度和情绪开放度。"}

## 当前建议

{"不要把群聊接梗直接当成暧昧信号；先锁定单一目标。" if summary["is_group"] else "先保持自然互动，补充具体聊天内容后再判断是否进入升温。"}
"""
    strategy = f"""---
slug: "{args.slug}"
updated_at: "{now}"
mode: "hybrid"
---

# 个性化追求策略

## 总原则

真诚为底，分寸为骨。先看趋势和密度，再做推进。

## 当前策略

{"群聊先转私聊、先确认身份、不要公开偏心某个人。" if summary["is_group"] else "从稳定聊天进入轻微专属感，不急着表白。"}
"""
    meta = {
        "name": args.name,
        "slug": args.slug,
        "created_at": now,
        "updated_at": now,
        "mode": "hybrid",
        "stage": stage,
        "score": score,
    }
    event = {
        "ts": now,
        "v": 1,
        "type": "profile_created",
        "slug": args.slug,
        "data": {
            "name": args.name,
            "source": "welive_jsonl_export",
            "path": str(export),
            "summary": summary,
        },
    }
    _write_text(crush_dir / "profile.md", profile)
    _write_text(crush_dir / "state.md", state)
    _write_text(crush_dir / "strategy.md", strategy)
    _write_text(crush_dir / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    _write_text(crush_dir / "events.jsonl", json.dumps(event, ensure_ascii=False) + "\n")
    _write_text(crush_dir / "interactions.jsonl", json.dumps({"ts": now, "v": 1, "type": "summary", "slug": args.slug, "data": summary}, ensure_ascii=False) + "\n")
    print(str(crush_dir))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="simp", description="Analyze WeLive/WeChat JSONL exports for simp memory files.")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="Print JSON summary for a WeLive export path.")
    inspect.add_argument("path", help="A .jsonl file or a record directory.")
    inspect.add_argument("--me", default=DEFAULT_ME, help="Your sender_username/wxid.")
    inspect.add_argument("--limit", type=int, default=10, help="Candidate count for group chats.")
    inspect.set_defaults(func=cmd_inspect)

    report = sub.add_parser("report", help="Write a Markdown report for a WeLive export path.")
    report.add_argument("path")
    report.add_argument("--name", default="聊天记录")
    report.add_argument("--me", default=DEFAULT_ME)
    report.add_argument("--limit", type=int, default=10)
    report.add_argument("--output", required=True)
    report.set_defaults(func=cmd_report)

    init = sub.add_parser("init-crush", help="Create a crush memory folder from a WeLive export path.")
    init.add_argument("path")
    init.add_argument("--name", required=True)
    init.add_argument("--slug", required=True)
    init.add_argument("--me", default=DEFAULT_ME)
    init.add_argument("--limit", type=int, default=10)
    init.add_argument("--root", default=DEFAULT_CRUSH_ROOT)
    init.set_defaults(func=cmd_init_crush)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
