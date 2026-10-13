# 重生之我是把妹王

`重生之我是把妹王` 是一个独立的本地项目，用来把微信聊天记录导出、结构化分析、追爱军师档案和 Codex 工作流串起来。

它不是 `simp-skill` 的简单复制，也不是 WeFlow 的二次打包。这个项目把所引用的上游能力组合成一个可维护的本地工作台：

- 用 WeFlow/WeLive 风格导出的微信 JSONL 作为聊天数据来源；
- 用 `simp-skill` 的追爱军师方法论和记忆结构做关系分析；
- 用 `goutoujunshi`（狗头军师）作为更高优先级的关系判断、话术与安全边界层；
- 用本项目的 Python CLI 解析导出、生成报告、建立本地档案；
- 由 Codex 直接读取源码和本地私有目录完成分析。

> 工程内部仍保留 `simp` 作为 Python 包名、CLI 命令和 `/simp` skill 指令名。这是为了兼容上游 `simp-skill`、现有测试和命令入口；对外项目名使用「重生之我是把妹王」。

## 上游引用

本项目引用并保留以下上游仓库快照：

- 微信聊天导出工具：WeFlow v5.0.0 完整源码快照，位于 `vendor/WeFlow/`；来源提交与恢复说明见 `vendor/WeFlow/UPSTREAM_SOURCE.md`
- 追爱军师 Skill：[BeamusWayne/simp-skill](https://github.com/BeamusWayne/simp-skill)，位于 `vendor/simp-skill/`
- 狗头军师 Skill：[shengjidaguai-china/goutoujunshi](https://github.com/shengjidaguai-china/goutoujunshi)，位于 `vendor/goutoujunshi/`；来源提交与验证说明见 `vendor/goutoujunshi/UPSTREAM_SOURCE.md`

根目录下的 `SKILL.md`、`prompts/`、`tools/`、`tests/` 也来自 `simp-skill`，并作为本项目的分析能力基础保留。

## 技能分层与优先级

本项目同时接入两套关系分析技能，并固定以下优先级（从高到低）：

1. 本仓库安全、隐私与本地输出 SOP
2. `goutoujunshi`（狗头军师）：方法论、证据分级、情绪支持、话术、伦理与安全边界
3. `simp`（追爱军师）：`/simp` 指令、`crushes/` 档案、事件流、CLI 与聊天解析
4. WeFlow：微信记录导出

方法论或建议冲突时默认采纳狗头军师；目录、命名、隐私与 `local_outputs/` 路由仍以本仓库 SOP 为准。完整冲突裁决、按需加载规则与数据边界见 [`docs/agent/SKILL_INTEGRATION.md`](docs/agent/SKILL_INTEGRATION.md)。

## 图形化界面

保留图形化导出流程。

WeFlow 的完整图形化应用源码、Windows 本地运行组件和导出实现保存在 `vendor/WeFlow/`。按该目录的 README 与 `package.json` 构建并运行后，可以通过 WeFlow/WeLive 图形化界面导出微信聊天记录，得到类似这样的目录：

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
simp/                       # 项目展示名：重生之我是把妹王
  src/simp_project/          # 本项目 CLI 和 JSONL 解析代码
  SKILL.md                   # 追爱军师 skill 入口
  prompts/                   # 追爱军师分析提示词
  tools/                     # simp-skill 原始辅助工具
  tests/                     # 测试
  vendor/WeFlow/             # WeFlow 上游快照
  vendor/simp-skill/         # simp-skill 上游快照
  vendor/goutoujunshi/       # 狗头军师上游快照（更高优先级技能）
  docs/wechat-export/        # 微信导出说明
  local_data/                # 本地私有数据，git 忽略
  local_outputs/             # 分类存放本地私有报告，git 忽略
  docs/agent/                # 本地输出 SOP 与技能分层规则
  .env                       # 本机私有配置，git 忽略
  .env.example               # 环境变量模板，可提交
```

`local_outputs/` 根目录不直接放文件。生成物按“会话类型 → 对象 slug → 分析领域”分类：

```text
local_outputs/
  private-chats/<contact-slug>/
    overview/
    language/
    timeline/
    relationship/
    visuals/
  group-chats/<chat-slug>/
  cross-chat/<analysis-slug>/
  system/
```

完整规则见 [`docs/agent/LOCAL_OUTPUTS_SOP.md`](docs/agent/LOCAL_OUTPUTS_SOP.md)。

## 安装

在项目根目录执行：

```powershell
cd D:\Coding\rizz-reborn
python -m pip install -e .
```

也可以不安装，直接使用源码模式：

```powershell
$env:PYTHONPATH = "D:\Coding\rizz-reborn\src"
python -m simp_project.cli --help
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
python -m simp_project.cli inspect "local_data\welive-records\demo-chat"
```

如果已经安装为 editable package，也可以用脚本入口。命令名仍为 `simp`：

```powershell
simp inspect "local_data\welive-records\demo-chat"
```

### 3. 生成 Markdown 报告

```powershell
python -m simp_project.cli report "local_data\welive-records\demo-chat" `
  --name "示例对象" `
  --output "local_outputs\private-chats\demo-chat\overview\wechat-summary.md"
```

### 4. 建立本地档案

```powershell
python -m simp_project.cli init-crush "local_data\welive-records\demo-chat" `
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

- `src/simp_project/` 的解析代码
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

`local_outputs/` 内的文件还必须遵守 [`docs/agent/LOCAL_OUTPUTS_SOP.md`](docs/agent/LOCAL_OUTPUTS_SOP.md)，禁止把生成物散落在根目录。

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

狗头军师快照自带结构校验，可单独运行：

```powershell
python vendor\goutoujunshi\scripts\validate_skill.py
python vendor\goutoujunshi\scripts\validate_skill.py --runtime
```

## 备注

`vendor/WeFlow/` 固定保留 WeFlow v5.0.0 完整源码快照。更新该快照时必须同步 `vendor/WeFlow/UPSTREAM_SOURCE.md` 中的来源提交、文件清单验证结果和安全说明。

`vendor/goutoujunshi/` 固定保留狗头军师快照。更新该快照时必须同步 `vendor/goutoujunshi/UPSTREAM_SOURCE.md` 中的来源提交、文件数验证结果和许可说明，并重跑上面的校验命令。优先级规则只在 `SKILL.md` 与 `docs/agent/SKILL_INTEGRATION.md` 中维护，不要直接改快照内容。
