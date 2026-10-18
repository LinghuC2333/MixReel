<h1 align="center">MixReel</h1>

<h3 align="center">把一条参考短视频，翻拍成你自己的故事</h3>

<p align="center">一个 Agent Skill，用你自己的角色和音乐，把参考视频改编成新的卡点短片</p>

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

这是一个给 Claude Code、Codex 等助手用的 Agent Skill。把参考视频、目标音乐和故事资料交给助手，它会逐镜拆解参考视频带给观众的感受，在你的故事里找到对应的情节，产出可以逐镜审阅的脚本、关键帧、视频片段和卡着音乐剪好的成片。

搬过来的是参考视频的观看体验，人物、故事和画风都换成你自己的。

<p align="center">
  <img src="https://github.com/LinghuC2333/mixreel/releases/download/showcase-first-meeting/side-by-side.webp" alt="左边是参考视频，右边是用这个 skill 做出的新短片" width="608">
</p>
<p align="center"><em>左边是参考视频，右边是给我们自己的小说做的 16.5 秒短片。</em></p>

## 安装

```bash
npx skills add LinghuC2333/mixreel
```

也可以把 `skills/mixreel` 整个目录复制到助手的技能目录，Claude Code 项目一般是 `.claude/skills`，Codex 一般是 `~/.codex/skills`。

skill 本身免费。生图和生视频用的是你自己选、自己付费的服务，在本机配置一次就行，见下文“配置自己的模型”。

## 案例

### The Last Princess · 初遇

[制作说明（英文）](docs/showcase/first-meeting/README.md) · [参考视频原片](https://github.com/LinghuC2333/mixreel/releases/download/showcase-first-meeting/reference.mp4) · [带声音的完整成片](https://github.com/LinghuC2333/mixreel/releases/download/showcase-first-meeting/first-meeting.mp4)

<table>
  <tr>
    <td>
      <p><b>“初遇”</b>就是页面顶部那条视频，给言情小说《The Last Princess》做的 16.5 秒竖版短片。参考视频是一段灰阶手绘的舞会邂逅，她毫无察觉，他在人群里一眼认出她。我们把这种感觉搬到了叛军攻进王宫的那一夜。他在楼梯上认出公主，抓住她的手腕，她甩了他一巴掌逃走，留下他脸上的掌印和嘴角一点笑意。</p>
      <p>一共 6 个镜头、8 张关键帧。用户选择沿用参考视频的画风，所以直接拿参考视频的帧当 Ideogram 4.5 的编辑底图，用官方角色立绘保证人物长相。两处手画坏了，交给 GPT Image 2.5 局部修补。视频用 MiniMax H3 生成，768P。切点落在鼓点进入、全曲最重的鼓点和收尾两下重拍上，剪成每秒 12 张画的一拍二节奏。</p>
      <p>只算成片里用到的部分，图片约 <b>2.10 美元</b>，视频约 <b>13 元</b>。算上全部试错，图片约 7.30 美元，视频 16.20 元。这些是服务商的报价和估算，还没和账单核对。</p>
    </td>
  </tr>
</table>

<p align="center">
  <img src="https://github.com/LinghuC2333/mixreel/releases/download/showcase-first-meeting/process.jpg" alt="三个镜头从参考帧到关键帧再到成片" width="760">
</p>
<p align="center"><em>六个镜头里挑了三个，从参考帧到关键帧再到成片。</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/mixreel/releases/download/showcase-first-meeting/keyframes.jpg" alt="短片的 8 张关键帧" width="760">
</p>
<p align="center"><em>全部 8 张关键帧。同一场戏里，每个角色的脸和衣服前后一致。</em></p>

参考视频和配乐片段 “Own The Dark” 的权利归原作者所有，这里只用来演示流程。

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

## 它做了什么

**从观众感受出发写脚本。** 助手先把参考视频拆成镜头，记下观众每一刻在期待什么、知道了什么、感受到什么，再去你的故事里找能制造同样感受的情节，标明出处，标出哪些压缩了、哪些是新加的。脚本交给你之前，还会先假装一个没看过原著的观众过一遍。

**能直接审阅的场景描述。** 每个镜头只有一个主要机位，动作按因果顺序写成看得见的画面，写清结尾停在哪，只保留现场声。容易生成失败的动作会拆成起始状态、接触、变化、结果四步。你审的是画面，不是模型咒语。

**按视频模型分别写提示词。** MiniMax H3 用六段式参考提示词，图片编号严格对应实际上传顺序；Seedance 2 用简短的单机位描述。两套各写各的，不互相转换。

**保住画风和角色的关键帧。** 每个镜头选一张构图参考，先出简易构图稿，再用你的画风和角色参考补完，最后做局部修补。参考视频里如果已经有合适的帧，可以直接当编辑底图，它算不算画风参考由你决定。

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
skills/mixreel/
  SKILL.md        入口、阶段选择与边界
  references/     故事、分镜、图像、视频和执行说明，按阶段读取
  scripts/        本地分析、剪辑导出、计划检查、费用记录与脱敏
  assets/         项目记录模板和合成计划样例
tests/            不触发付费调用的自动测试
docs/             设计说明、验证记录和案例说明
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
