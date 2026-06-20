from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable

CN_TZ = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class Message:
    ts: int
    local_id: int
    sender: str
    real_sender_id: str
    local_type: str
    content: str
    raw: dict

    @property
    def dt(self) -> datetime:
        return datetime.fromtimestamp(self.ts, CN_TZ)


def find_jsonl(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_file():
        return candidate
    files = sorted(candidate.rglob("*.jsonl"), key=lambda p: p.stat().st_size, reverse=True)
    if not files:
        raise FileNotFoundError(f"No .jsonl export found under {candidate}")
    return files[0]


def load_messages(path: str | Path) -> list[Message]:
    export = find_jsonl(path)
    messages: list[Message] = []
    with export.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no} in {export}") from exc
            try:
                ts = int(raw.get("create_time") or 0)
            except (TypeError, ValueError):
                ts = 0
            try:
                local_id = int(raw.get("local_id") or 0)
            except (TypeError, ValueError):
                local_id = 0
            messages.append(
                Message(
                    ts=ts,
                    local_id=local_id,
                    sender=raw.get("sender_username") or "SYSTEM",
                    real_sender_id=str(raw.get("real_sender_id") or ""),
                    local_type=str(raw.get("local_type") or ""),
                    content=raw.get("message_content") or "",
                    raw=raw,
                )
            )
    messages.sort(key=lambda m: (m.ts, m.local_id))
    return messages


def is_group_export(messages: Iterable[Message]) -> bool:
    senders = {m.sender for m in messages if m.sender not in {"", "SYSTEM"}}
    return len(senders) > 2


def daily_counts(messages: Iterable[Message]) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for msg in messages:
        counts[msg.dt.date().isoformat()][msg.sender] += 1
    return dict(counts)


def adjacent_interactions(
    messages: list[Message],
    me: str,
    window_seconds: int = 900,
) -> list[dict]:
    total = Counter(m.sender for m in messages if m.sender not in {me, "SYSTEM", ""})
    by_sender_id: dict[str, str] = {}
    for msg in messages:
        if msg.sender not in {me, "SYSTEM", ""} and msg.sender not in by_sender_id:
            by_sender_id[msg.sender] = msg.real_sender_id

    they_after_me: Counter = Counter()
    me_after_them: Counter = Counter()

    previous: Message | None = None
    for msg in messages:
        if msg.sender in {"SYSTEM", ""}:
            continue
        if previous and msg.sender != previous.sender:
            gap = msg.ts - previous.ts
            if 0 <= gap <= window_seconds:
                if previous.sender == me and msg.sender != me:
                    they_after_me[msg.sender] += 1
                elif msg.sender == me and previous.sender != me:
                    me_after_them[previous.sender] += 1
        previous = msg

    rows = []
    for sender, count in total.items():
        adjacent = they_after_me[sender] + me_after_them[sender]
        rows.append(
            {
                "sender": sender,
                "real_sender_id": by_sender_id.get(sender, ""),
                "messages": count,
                "adjacent_interactions": adjacent,
                "after_me": they_after_me[sender],
                "me_after": me_after_them[sender],
                "score": adjacent * 10 + count * 0.1,
            }
        )
    rows.sort(key=lambda row: row["score"], reverse=True)
    return rows


def reply_latencies(messages: list[Message], sender_a: str, sender_b: str, max_gap_seconds: int = 21600) -> dict:
    values: list[int] = []
    previous: Message | None = None
    for msg in messages:
        if msg.sender in {"SYSTEM", ""}:
            continue
        if previous and previous.sender == sender_a and msg.sender == sender_b:
            gap = msg.ts - previous.ts
            if 0 <= gap <= max_gap_seconds:
                values.append(gap)
        previous = msg
    if not values:
        return {"count": 0}
    values.sort()
    return {
        "count": len(values),
        "median_seconds": statistics.median(values),
        "mean_seconds": round(statistics.mean(values), 2),
        "under_60_seconds": sum(v <= 60 for v in values),
        "under_300_seconds": sum(v <= 300 for v in values),
    }


def summarize(messages: list[Message], me: str, candidate_limit: int = 10) -> dict:
    if not messages:
        raise ValueError("No messages to summarize")
    sender_counts = Counter(m.sender for m in messages)
    type_counts = Counter(m.local_type for m in messages)
    group = is_group_export(messages)
    summary = {
        "range_start": messages[0].dt.isoformat(),
        "range_end": messages[-1].dt.isoformat(),
        "total_messages": len(messages),
        "message_types": dict(type_counts.most_common()),
        "sender_counts": dict(sender_counts.most_common(30)),
        "my_messages": sender_counts.get(me, 0),
        "system_messages": sender_counts.get("SYSTEM", 0) + sender_counts.get("", 0),
        "active_senders": len([s for s in sender_counts if s not in {me, "SYSTEM", ""}]),
        "is_group": group,
    }
    if group:
        summary["candidates"] = adjacent_interactions(messages, me)[:candidate_limit]
    else:
        others = [s for s in sender_counts if s not in {me, "SYSTEM", ""}]
        if others:
            other = max(others, key=lambda s: sender_counts[s])
            summary["target_sender"] = other
            summary["reply_target_after_me"] = reply_latencies(messages, me, other)
            summary["reply_me_after_target"] = reply_latencies(messages, other, me)
    return summary


def render_markdown_report(name: str, source: Path, summary: dict) -> str:
    lines = [
        f"# {name} 微信导出分析",
        "",
        f"数据来源：`{source}`",
        f"范围：{summary['range_start']} 到 {summary['range_end']}",
        "",
        "## 概览",
        "",
        f"- 总消息：{summary['total_messages']}",
        f"- 我的消息：{summary['my_messages']}",
        f"- 系统消息：{summary['system_messages']}",
        f"- 活跃发言人：{summary['active_senders']}",
        f"- 导出类型：{'群聊' if summary['is_group'] else '私聊'}",
        "",
    ]
    if summary["is_group"]:
        lines.extend(["## 候选互动对象", ""])
        for idx, row in enumerate(summary.get("candidates", []), start=1):
            lines.append(
                f"{idx}. `{row['sender']}`：总 {row['messages']} 条；"
                f"相邻互动 {row['adjacent_interactions']} 次；"
                f"ta 接我 {row['after_me']} 次；我接 ta {row['me_after']} 次。"
            )
        lines.extend(
            [
                "",
                "## 判断",
                "",
                "这是群聊公共场域，候选互动只能说明社交热度和话题邻近度，不能直接等同于恋爱信号。建议先锁定单一目标，再抽取私聊或连续互动片段。",
            ]
        )
    else:
        lines.extend(
            [
                "## 私聊对象",
                "",
                f"- 目标 sender：`{summary.get('target_sender', '')}`",
                f"- ta 回我：{summary.get('reply_target_after_me', {})}",
                f"- 我回 ta：{summary.get('reply_me_after_target', {})}",
                "",
                "## 判断",
                "",
                "这是 1v1 私聊，可以继续结合内容关键词、主动重启会话和私密话题开放度做追爱信号分析。",
            ]
        )
    lines.append("")
    return "\n".join(lines)

