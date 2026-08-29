# 本地输出分类 SOP / Local Outputs Organization SOP

本 SOP 规定私有分析生成物在 `local_outputs/` 下的存放方式，适用于 Codex、项目脚本和手工分析任务。

## 目标

- 输出根目录不得散落文件。
- 按会话范围、对象和分析领域组织生成物。
- 原始聊天导出与生成分析严格分离。
- 保持本地隐私，并让后续清理、重跑和复核有稳定路径。

## 标准目录

```text
local_outputs/
  private-chats/
    <contact-slug>/
      overview/       # 综合互动与关系摘要
      language/       # 词频、话题、情感和语言风格
      timeline/       # 日/周趋势和回复时间分析
      relationship/   # 阶段、信号、风险和推进策略
      visuals/        # 图表及其他渲染媒体
  group-chats/
    <chat-slug>/
      overview/
      participants/
      language/
      timeline/
      visuals/
  cross-chat/
    <analysis-slug>/  # 跨多个会话的分析
  system/
    audits/           # 隐私、完整性和工作流审计
    logs/             # 必要时保存脱敏的本地执行摘要
```

只创建当前任务实际使用的目录，不预建空目录树。

## 命名规则

1. 目录和文件名统一使用小写 ASCII `kebab-case`。
2. 对象目录使用稳定 slug，例如 `liu-na-luna`；不得使用原始微信 ID 作为目录名。
3. 文件按分析用途命名，不重复联系人名；对象已经由父目录表达。
4. 同一分析的人类可读版与机器可读版使用相同文件主名并放在一起：

   ```text
   overview/relationship-analysis.md
   overview/relationship-analysis.json
   ```

5. 禁止把生成文件直接写在 `local_outputs/` 根目录。

## 数据边界

- 微信/WeFlow 原始导出放在 `local_data/welive-records/<subject-slug>/`。
- 关系档案与状态放在 `local_data/crushes/<subject-slug>/`。
- 报告、聚合数据、表格和可视化放在 `local_outputs/`。
- 一次性私有分析脚本放在 `local_data/tools/`；可复用且不含隐私的代码进入受跟踪源码。
- 报告默认不得复述私聊原文，优先输出计数、区间、百分比和抽象摘要。

## 输出路由流程

生成文件前依次执行：

1. 确定范围：`private-chats`、`group-chats`、`cross-chat` 或 `system`。
2. 解析或建立稳定的对象/分析 slug。
3. 确定领域：`overview`、`language`、`timeline`、`relationship`、`visuals`，或最接近的群聊/系统分类。
4. 在 `local_outputs/<scope>/<slug>/<domain>/` 下构造目标路径。
5. 验证解析后的绝对目标仍位于仓库 `local_outputs/` 根目录内。
6. 生成文件，并验证非空且被 Git 忽略。

示例：

```powershell
$output = "local_outputs\private-chats\example\overview\wechat-summary.md"
python -m simp_project.cli report "local_data\welive-records\example" `
  --name "示例" `
  --output $output
git check-ignore -v -- $output
```

## 迁移流程

整理已有私有产物时：

1. 列出精确源文件与目标映射。
2. 移动前解析并校验输出根目录的绝对路径。
3. 使用明确的 literal path 移动，不使用宽泛通配符或 `git clean`。
4. 验证每个目标文件存在且非空。
5. 验证旧文件路径已不存在。
6. 确认 `local_outputs/` 根目录不再有散落文件。
7. 运行仓库 Markdown 链接审计；没有现成脚本时执行定向链接与引用扫描。

## 完成检查

```powershell
# 根目录只能包含目录。
Get-ChildItem -LiteralPath "local_outputs" -File

# 私有产物必须继续被忽略。
git check-ignore -v -- "local_outputs\private-chats\example\overview\wechat-summary.md"

# 检查受跟踪改动，确认私有产物没有进入 Git。
git status --short --ignored
git diff --check
```

如果 `Get-ChildItem ... -File` 返回任何文件，必须先完成分类和迁移再结束任务。
