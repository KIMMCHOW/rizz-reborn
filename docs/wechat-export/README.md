# 微信导出工作流

本项目的工作流分成两段：

1. 图形化导出：使用 WeFlow/WeLive 导出微信聊天记录。
2. 源码分析：Codex 或 Python 读取 JSONL 导出并生成分析结果。

## 上游 GUI

图形化界面保留在 WeFlow 这一层。

本项目引用 [hicccc77/WeFlow](https://github.com/hicccc77/WeFlow) 作为微信聊天导出工具，上游快照位于：

```text
vendor/WeFlow/
```

WeFlow 上游 README 中说明了 GUI 应用、Releases 下载、HTTP API、开发模式等信息。本项目不把 GUI 打包成自己的 exe，也不替代 WeFlow；本项目负责导出后的结构化解析和关系分析。

## 导出位置

导出的聊天记录建议放在本地私有目录：

```text
local_data/welive-records/
```

常见结构：

```text
local_data/welive-records/
  someone/
    wxid_xxx_123.jsonl
    wxid_xxx_123_media/
  some-group/
    48250421441@chatroom_xxx.jsonl
    48250421441@chatroom_xxx_media/
```

这些目录包含个人隐私，已经被 `.gitignore` 忽略。

## 配置

复制 `.env.example` 到 `.env`：

```powershell
Copy-Item .env.example .env
```

设置自己的 sender id：

```env
SIMP_ME_WXID=wxid_me
SIMP_CRUSH_ROOT=local_data/crushes
SIMP_WELIVE_RECORD_DIR=local_data/welive-records
SIMP_OUTPUT_DIR=local_outputs
```

注意：`.env` 会被 CLI 自动读取，但 PowerShell 不会自动把 `.env` 变成 `$env:*`。所以文档示例直接使用 `local_data\...` 路径。

## 查看导出摘要

```powershell
python -m rizz_reborn.cli inspect "local_data\welive-records\some-chat"
```

CLI 可以接收 `.jsonl` 文件，也可以接收包含 `.jsonl` 的父目录。传入目录时，会默认选择该目录下最大的 `.jsonl` 文件。

## 生成报告

```powershell
python -m rizz_reborn.cli report "local_data\welive-records\some-chat" `
  --name "示例" `
  --output "local_outputs\example.md"
```

## 建立本地档案

```powershell
python -m rizz_reborn.cli init-crush "local_data\welive-records\some-chat" `
  --name "示例" `
  --slug "example"
```

默认输出到 `.env` 中的 `SIMP_CRUSH_ROOT`，通常是：

```text
local_data/crushes/example/
```

## 群聊与私聊

私聊导出会统计双方消息量和回复延迟。

群聊导出会先做社交图谱初筛，按与你相邻互动的密度给出候选成员排序。群聊里的接梗、夸赞和活跃互动不能直接当成恋爱信号，需要进一步锁定单一对象，最好迁移到私聊或截取连续互动片段再分析。

## Codex 使用方式

Codex 应直接读取项目源码：

- `src/rizz_reborn/`
- `SKILL.md`
- `prompts/`
- `.env`
- `local_data/`

分析结果写入：

- `local_data/crushes/`
- `local_outputs/`

不要生成单 exe，也不要把原始聊天记录、档案和报告加入 Git。
