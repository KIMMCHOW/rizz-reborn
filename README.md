# rizz-reborn

`rizz-reborn`（中文名：重生之我是把妹王）是一个独立的本地项目，用来把微信聊天记录导出、结构化分析、追爱军师档案和 Codex 工作流串起来。

它不是 `simp-skill` 的简单复制，也不是 WeFlow 的二次打包。这个项目把两个上游能力组合成一个可维护的本地工作台：

- 用 WeFlow/WeLive 风格导出的微信 JSONL 作为聊天数据来源；
- 用 `simp-skill` 的追爱军师方法论和记忆结构做关系分析；
- 用本项目的 Python CLI 解析导出、生成报告、建立本地档案；
- 由 Codex 直接读取源码和本地私有目录完成分析。

> 项目发行名和主 CLI 已改为 `rizz-reborn`，Python 模块名为 `rizz_reborn`。上游 `simp-skill` 自带的 `/simp` skill 指令名保持不变，`simp` CLI 也作为兼容别名保留。

## 上游引用

本项目引用并保留以下上游仓库快照：

- 微信聊天导出工具：[hicccc77/WeFlow](https://github.com/hicccc77/WeFlow)，位于 `vendor/WeFlow/`
- 追爱军师 Skill：[BeamusWayne/simp-skill](https://github.com/BeamusWayne/simp-skill)，位于 `vendor/simp-skill/`

根目录下的 `SKILL.md`、`prompts/`、`tools/`、`tests/` 也来自 `simp-skill`，并作为本项目的分析能力基础保留。

## 图形化界面

保留图形化导出流程。

WeFlow 上游仓库的图形化工具说明和资源保存在 `vendor/WeFlow/`。实际使用时，你可以通过 WeFlow/WeLive 图形化界面导出微信聊天记录，得到类似这样的目录：

```text
record/
  wxid_xxx_123/
    wxid_xxx_123.jsonl
    wxid_xxx_123_media/
  some-group/
    48250421441@chatroom_xxx.jsonl
    48250421441@chatroom_xxx_media/
```

导出完成后，Codex 或 Python CLI 读取 `.jsonl` 文件进行分析。不要把原始聊天记录提交到 Git。

## 功能

- 识别 WeFlow/WeLive JSONL 导出目录中的聊天记录文件
- 区分群聊和私聊
- 统计消息量、发言人、消息类型、回复速度
- 对群聊生成候选互动对象排序
- 对私聊生成基本回复时延统计
- 生成 Markdown 分析报告
- 生成 `simp-skill` 风格的本地档案目录
- 通过 `.env` 管理本机私有路径和自己的微信 sender id

## 项目结构

```text
rizz-reborn/                # 项目展示名：rizz-reborn
  src/rizz_reborn/           # 本项目 CLI 和 JSONL 解析代码
  SKILL.md                   # 追爱军师 skill 入口
  prompts/                   # 追爱军师分析提示词
  tools/                     # simp-skill 原始辅助工具
  tests/                     # 测试
  vendor/WeFlow/             # WeFlow 上游快照
  vendor/simp-skill/         # simp-skill 上游快照
  docs/wechat-export/        # 微信导出说明
  local_data/                # 本地私有数据，git 忽略
  local_outputs/             # 本地私有报告，git 忽略
  .env                       # 本机私有配置，git 忽略
  .env.example               # 环境变量模板，可提交
```

## 安装

在项目根目录执行：

```powershell
cd D:\Coding\simp
python -m pip install -e .
```

也可以不安装，直接使用源码模式：

```powershell
$env:PYTHONPATH = "D:\Coding\simp\src"
python -m rizz_reborn.cli --help
```

## 环境变量

复制 `.env.example` 为 `.env`，填入本机配置：

```powershell
Copy-Item .env.example .env
```

`.env` 示例：

```env
SIMP_ME_WXID=wxid_me
SIMP_CRUSH_ROOT=local_data/crushes
SIMP_WELIVE_RECORD_DIR=local_data/welive-records
SIMP_OUTPUT_DIR=local_outputs
```

变量说明：

- `SIMP_ME_WXID`：你自己的 `sender_username`，用于区分“我”和“对方”
- `SIMP_CRUSH_ROOT`：本地档案输出目录
- `SIMP_WELIVE_RECORD_DIR`：本地微信导出记录目录
- `SIMP_OUTPUT_DIR`：本地报告输出目录

`.env` 已被 `.gitignore` 忽略。

## 使用流程

### 1. 用图形化界面导出微信记录

使用 WeFlow/WeLive 图形化界面导出聊天记录。导出结果建议放在：

```text
local_data/welive-records/
```

例如：

```text
local_data/welive-records/demo-chat/48250421441@chatroom_xxx.jsonl
local_data/welive-records/someone/wxid_xxx.jsonl
```

### 2. 查看导出摘要

```powershell
python -m rizz_reborn.cli inspect "local_data\welive-records\demo-chat"
```

如果已经安装为 editable package，也可以用脚本入口。主命令名为 `rizz-reborn`：

```powershell
rizz-reborn inspect "local_data\welive-records\demo-chat"
```

旧的 `simp inspect ...` 仍可作为兼容别名使用。

### 3. 生成 Markdown 报告

```powershell
python -m rizz_reborn.cli report "local_data\welive-records\demo-chat" `
  --name "示例对象" `
  --output "local_outputs\demo.md"
```

### 4. 建立本地档案

```powershell
python -m rizz_reborn.cli init-crush "local_data\welive-records\demo-chat" `
  --name "示例对象" `
  --slug "demo"
```

生成结构：

```text
local_data/crushes/demo/
  profile.md
  state.md
  strategy.md
  events.jsonl
  interactions.jsonl
  memories/chats/
```

### 5. 让 Codex 继续分析

Codex 在本项目中应直接读取：

- `src/rizz_reborn/` 的解析代码
- `SKILL.md` 和 `prompts/` 的分析规则
- `.env` 中配置的私有目录
- `local_data/crushes/` 中的本地档案

不需要也不应该打包成单个 `.exe`。

## 隐私规则

以下内容是私有数据，不能提交到 Git：

- `.env`
- `local_data/`
- `local_outputs/`
- `data/`
- `outputs/`
- `*.jsonl`
- 微信导出的媒体文件、语音、图片

`.gitignore` 已经覆盖这些路径。提交前可以检查：

```powershell
git status --short --ignored
```

可提交的应当是源码、文档、测试和上游源码快照；不可提交的是聊天记录、分析档案、报告和本机配置。

## 开发与测试

运行测试：

```powershell
python -m pytest -q
```

当前测试范围通过 `pytest.ini` 限定在根目录 `tests/`，避免重复收集 `vendor/simp-skill/tests/`。

## 备注

`vendor/WeFlow/` 当前保留的是上游仓库公开快照。若上游后续补充完整源码或发布新的图形化工具代码，可以更新该目录并同步 README 中的说明。
