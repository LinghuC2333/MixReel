<h1 align="center">MixReel</h1>

<h3 align="center">把一条参考短视频，翻拍成你自己的故事</h3>

<p align="center">一组可分别调用的 skill，用于参考分析、脚本、人物一致的插画和视频制作</p>

<p align="center">
  <a href="#安装"><strong>安装</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#案例"><strong>案例</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#怎么用"><strong>怎么用</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="./README.md"><strong>English</strong></a>
</p>

<p align="center">
  <a href="./LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue?style=flat-square"></a>
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-Claude%20Code%20%7C%20Codex-6E56CF?style=flat-square">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="ffmpeg" src="https://img.shields.io/badge/ffmpeg-required-007808?style=flat-square">
</p>

MixReel 包含七个给 Claude Code、Codex 等助手用的 skill。提供参考视频和广告主或创作要求，可以只写脚本、单独完成某个阶段，也可以使用自己选择的素材和模型完成整片。

借鉴范围由你决定，可以选择钩子、脚本、构图，也可以选择音乐、剪辑或画风。借用其中一项，不会自动把其他项一起搬来。

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/side-by-side.webp" alt="左边是参考视频，右边是用这个 skill 做出的新短片" width="608">
</p>
<p align="center"><em>左边是参考视频，右边是用这个 skill 做出的新短片。</em></p>

## 安装

安装完整套件，再按需要单独调用某个 skill。先下载或克隆本仓库，在仓库目录执行下面的本地安装命令。

```bash
python3 scripts/install_collection.py --destination ~/.codex/skills
```

Claude Code 项目可把目标改为 `.claude/skills`。安装器一起复制七个 skill 和共用资源，不读取密钥、不联网，也不覆盖已有 MixReel。更新时先装到新目录检查，再自行替换旧安装；不要只复制某个专用 skill，或修改其他项目正在引用的目录。


skill 本身免费。生图和生视频用的是你自己选、自己付费的服务，在本机配置一次就行，见下文“配置自己的模型”。

## 案例

### 初遇

[参考视频原片](https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/reference.mp4) · [带声音的完整成片](https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/first-meeting.mp4)

一条 16.5 秒的竖版短片，就是页面顶部那条视频。参考视频是一段手绘风格的舞会邂逅，新版本讲的是另一场初遇，换成了自己的角色，保留参考视频的画风，按新的音乐卡点剪辑。

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/process.jpg" alt="三个镜头从参考帧到关键帧再到成片" width="760">
</p>
<p align="center"><em>六个镜头里挑了三个，从参考帧到关键帧再到成片。</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/keyframes.jpg" alt="短片的 8 张关键帧" width="760">
</p>
<p align="center"><em>全部 8 张关键帧。同一场戏里，每个角色的脸和衣服前后一致。</em></p>

### 第一人称视角

[参考视频原片](https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/reference.mp4) · [带声音的完整成片](https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/pov-short.mp4)

一条 15.8 秒的竖版短片，镜头就是观众的眼睛。参考视频是一段游戏角色的粉丝剪辑，每句歌词一个特写，她的手伸进画面，他一直看着镜头。新版本保留这种第一人称的心动，换成了自己的角色和场景，画风用官方角色立绘，不沿用参考视频的画风。

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/side-by-side.webp" alt="左边是参考视频，右边是新短片" width="608">
</p>
<p align="center"><em>左边是参考视频，右边是新短片。</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/process.jpg" alt="两个镜头从构图参考到简易稿、关键帧再到成片" width="760">
</p>
<p align="center"><em>八个镜头里挑了两个，从构图参考到简易稿、关键帧再到成片。简易稿就已经带上了选定的色调和光线。</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/keyframes.jpg" alt="短片的 8 张关键帧" width="760">
</p>
<p align="center"><em>全部 8 张关键帧，每句歌词一张。</em></p>

两个案例中的参考视频和配乐，权利都归原作者所有，这里只用来演示流程。

## 怎么用

在一个私人项目文件夹里启动助手，把参考视频、音乐和故事资料放进去，直接用大白话说。

只要方案，不生成、不花钱。

```text
使用 $mixreel。参考视频 ./media/reference.mp4，音乐 ./media/music.mp3，
故事资料在 ./story/。给我两三版可以逐镜审阅的脚本。
```

带审阅节点地完整制作。

```text
使用 $mixreel，把已经确认的脚本做成成片。
简易构图稿出完、关键帧和视频预算出来、最后剪辑之前，各停一次等我确认。
```

助手会把每个决定、每次输入和每笔费用记在项目文件夹里，任何一步停下来都能接着做。

也可以直接使用 `$mixreel-script` 写广告脚本，或用 `$mixreel-review` 检查已有素材，其他入口见下方项目结构。

## 它做了什么

**结合参考和目标写脚本。** 助手分析具体的开头、揭露和回应，再决定哪些适合表达你的信息。广告脚本包含实际画面、准确文案、产品行为和品牌界面的呈现方式。改编故事时注明来源和新写情节。单独写脚本不需要生成素材或配置模型账号。

**能直接审阅的场景描述。** 每个镜头有明确的运镜，动作按因果顺序写成看得见的画面，写清结尾停在哪。容易生成失败的动作会说明起始状态、接触、变化和结果。字幕、配乐、产品界面和品牌要求保留在脚本与后期计划中，不会因为某种模型提示词排除它们就从成片删掉。

**按视频模型分别写提示词。** MiniMax H3 用六段式参考提示词，图片编号严格对应实际上传顺序；Seedance 2 用简短的单机位描述。两套各写各的，不互相转换。

**保住画风和角色的关键帧。** 先确定连贯段落需要哪些图，已有素材可以复用，多个镜头也可以共用一张关键帧。每张必要的新关键帧只分两步。先拿一张构图图、你的画风参考和角色参考生图，再做局部修改。构图图可以来自可选的三维站位预演，也可以是参考视频里合适的一帧。每一步按模型的长处选，比如 Ideogram 擅长迁移画风，GPT 擅长照着具体指令改图；每一步出完都会核对图片确实改了。参考帧算不算画风参考由你决定。

**相连镜头合在一次生成里。** 先排好整段动作，再按接口能力把多个镜头放进同一次请求，使用少量关键帧、脚本和受支持的视频及音频参考。需要拆开时记录原因，并比较最低计费时长和返工费用。动作速度单独说明，快速动作不必占满整段视频。

**按实际动作卡点。** 助手会看生成回来的片段，找到每个动作真正发生的时刻，再对到拍子上。本地剪辑脚本负责剪切、变速、一拍二和配乐。

**花钱可追溯。** 报价、估算和实际扣款分开记。付费请求发出前先落盘，超时之后不会盲目重交。

## 配置自己的模型

生图、编辑图片和生成视频可以用不同的服务。先在仓库外创建空白的私人配置，这条命令不联网，也不导入任何密钥。

```sh
python3 skills/mixreel/scripts/init_config.py
```

```text
~/.config/mixreel/
├── providers.json      # 服务、模型、接口地址和密钥名称
└── credentials.json    # 你自己的密钥，只保存在本机
```

助手怎么读取这些配置，见[本机配置说明](skills/mixreel/references/local-config.md)。仓库不附带付费模型的客户端，助手使用自己已有的工具或你配置的接口，并先核实当前的参数和价格。

## 项目结构

```text
skills/
  mixreel/             coordinator and shared rules, tools, templates
  mixreel-analyze/     reference video and audio evidence
  mixreel-script/      adaptation and advertising scripts
  mixreel-keyframes/   consistent illustration keyframes
  mixreel-video-plan/  generation groups and model prompts
  mixreel-produce/     authorized generation, edit and export
  mixreel-review/      evidence-based review and repair routing
  mixreel.collection.json
```

## 工具与检查

Python 3.10 及以上即可运行计划检查、费用记录和脱敏工具。媒体诊断和剪辑导出需要 `ffmpeg` 和 `ffprobe`，拍点分析另需 `numpy` 和 `librosa`。

```sh
python3 skills/mixreel/scripts/validate_plan.py skills/mixreel/assets/plan.example.json
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

## 参与贡献

修改创作方法时，请附上真实任务里的观察和人工审阅依据。供应商专用的支持放到独立的适配部分，附上当前文档依据和不触发付费的测试。不要把密钥、签名链接或未经授权的他人素材放进仓库。[设计说明](docs/DESIGN.md)解释各项取舍，[验证记录](docs/VALIDATION.md)区分已经跑过的检查和尚未验证的部分。

## 许可证

MIT。许可证只覆盖本项目的原创文件，不授予案例中参考视频、音乐和角色素材的任何权利。
