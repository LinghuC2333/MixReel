# 从参考视频到故事短片

一个可用于 Codex、Claude Code 等支持 Agent Skills 的助手的技能项目。输入参考视频、目标音乐和故事资料，输出用户指定阶段的成果，可以只做提案，也可以继续制作关键帧与短片。

创作计划与接口配置分开。插画按构图参考、GPT 简易稿、Ideogram 完成插画、GPT 修正的顺序制作，具体接口由用户配置。主说明使用英文，便于跨团队复用；本说明和设计说明使用中文。

## 开始使用

将 `skills/reference-replica-video` 整个目录复制到助手的技能目录。Codex 通常使用 `~/.codex/skills`，Claude Code 项目通常使用 `.claude/skills`。实际加载方式以所用宿主为准。也可以让助手直接读取该目录中的 `SKILL.md`。

例如，让助手使用 `$reference-replica-video`，读取参考视频、目标音乐和小说资料，先提交可逐镜检查的提案。本例只授权提案，不会自动开始生图。

私人素材、项目记录和凭证放在这个源码目录以外。已做过的选择保存在项目记录中，继续任务时先读取这些记录。

## 配置自己的模型

生图、编辑图片和生成视频可以使用不同的服务，也可以共用同一服务。先运行下面的命令，在源码目录外创建空白配置。它不会联网或导入任何旧密钥。

```sh
python3 skills/reference-replica-video/scripts/init_config.py
```

随后在本机编辑这两个文件。

```text
~/.config/reference-replica-video/
├── providers.json      # 服务、模型、接口地址和密钥名称
└── credentials.json    # 用户自己的密钥，只保存在本机
```

填写所选服务的配置和密钥即可；已有宿主密钥管理或环境变量时可以直接沿用。初始化工具不会覆盖已存在的配置。macOS/Linux 默认只有当前用户能读取；Windows 需要自行设置文件访问权限。密钥文件采用明文存储，有现成的系统密钥管理工具时优先使用它。

仓库仅包含空白示例。助手或接口程序需按[本机配置说明](skills/reference-replica-video/references/local-config.md)读取相应配置；这个初始化命令本身不会连接服务或验证余额。

## 视频提示词

可编辑场景描述与发给模型的提示词分别保存。选择 Seedance 2 时使用简洁场景描述；选择 MiniMax H3 时，直接把已批准的场景、镜头计划与有序参考图写成六段提示词。两套写法按模型选择，不串联运行。

规则由用户授权的 Lunaverse IDE 文件改编，已移除专用执行命令和特定小说案例。具体迁入内容见[提示词来源与修改](docs/PROMPT-SOURCES.md)。接口的时长、字符限制、模型名称与收费仍需使用前核实。

## 项目结构

```text
skills/reference-replica-video/
  SKILL.md                  入口、阶段选择与必要约束
  references/               故事、分镜、图像、视频和执行说明
  scripts/                  本地分析、计划检查、费用记录与脱敏
  assets/                   项目记录模板和合成计划样例
  agents/                   Codex 显示信息
tests/                     无付费调用的自动测试
evals/                     真实任务验证方法和人工审阅维度
docs/                      设计、迁移与验证记录
```

## 工具与边界

Python 3.10 及以上即可运行计划检查、记录和脱敏工具，无额外 Python 依赖。媒体诊断需要本机已有 `ffmpeg` 和 `ffprobe`。

```sh
python3 skills/reference-replica-video/scripts/validate_plan.py skills/reference-replica-video/assets/plan.example.json
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

本项目不附带付费模型客户端。助手使用宿主已有的工具或已配置接口，并先核实参数、参考图能力和实际扣费渠道。网络提交由这些工具负责；本地费用记录工具本身不能拦截绕过它的调用。

费用报价、估算和实际扣款分开记录。任务提交超时后先查原任务；下载失败时只重试下载。详情见 [执行说明](skills/reference-replica-video/references/execution.md)。

## 阅读与贡献

入口只加载当前阶段需要的说明。[设计说明](docs/DESIGN.md)解释取舍，[迁移说明](docs/MIGRATION.md)说明旧实现如何归位，[验证记录](docs/VALIDATION.md)区分已经跑过的检查与尚未开展的实战验证。

修改创作方法时附上真实任务的观察与人工审阅依据。供应商专用支持放到独立适配部分，附当前文档依据和不触发付费的测试。不要把客户素材、故事原文、内部地址、签名链接或密钥加入仓库。

采用 MIT 许可证。许可证只覆盖本项目原创文件，不赋予使用外部音乐、视频或角色素材的权利。
