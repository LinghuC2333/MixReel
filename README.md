<h1 align="center">MixReel</h1>

<h3 align="center">Remix any reel into your own story</h3>

<p align="center">An agent skill that turns a reference video into a new beat-synced short with your own characters</p>

<p align="center">
  <a href="#install"><strong>Install</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#showcase"><strong>Showcase</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="#use-the-skill"><strong>Use the skill</strong></a>
  &nbsp;&bull;&nbsp;
  <a href="./README.zh-CN.md"><strong>简体中文</strong></a>
</p>

<p align="center">
  <a href="./LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue?style=flat-square"></a>
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-Claude%20Code%20%7C%20Codex-6E56CF?style=flat-square">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="ffmpeg" src="https://img.shields.io/badge/ffmpeg-required-007808?style=flat-square">
</p>

MixReel is an Agent Skill for Claude Code, Codex and other agents that load skills. Give your agent a reference video, a music track and your story material. It studies what the reference makes the viewer feel shot by shot, finds the matching moment in your story, and produces a reviewable script, keyframes, video clips and a final cut timed to the music.

The skill carries over the experience of the reference. Your characters, your story and your chosen visual style replace everything else.

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/side-by-side.webp" alt="Reference video on the left, the new short made with this skill on the right" width="608">
</p>
<p align="center"><em>Left, the reference video. Right, a new short made with this skill.</em></p>

## Install

```bash
npx skills add LinghuC2333/MixReel
```

You can also copy `skills/mixreel` into your agent's skill directory, for example `.claude/skills` for a Claude Code project or `~/.codex/skills` for Codex.

The skill itself is free. Image and video generation run on services you choose and pay for, and you configure them once on your own machine (see [Configure your models](#configure-your-models)).

## Showcase

### First Meeting

[Reference video](https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/reference.mp4) · [Full short with sound](https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/first-meeting.mp4)

A 16.5-second vertical short, the video at the top of this page. The reference is a hand-drawn ballroom meet-cute. The new version tells a different first meeting with its own characters, keeps the reference's look and is cut to new music.

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/process.jpg" alt="Reference frame, keyframe and frames from the final video for three shots" width="760">
</p>
<p align="center"><em>From reference frame to keyframe to final video, for three of the six shots.</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/keyframes.jpg" alt="The eight keyframes of the short" width="760">
</p>
<p align="center"><em>All eight keyframes. Each character keeps one face and one outfit across the scene.</em></p>

The reference video and the music belong to their owners and appear here only to demonstrate the workflow.

## Use the skill

Start your agent in a private project folder that holds your reference video, music and story notes, then ask in plain words.

Ask for a proposal only. Nothing is generated and nothing is paid for.

```text
Use $mixreel. Reference video ./media/reference.mp4, music ./media/music.mp3,
story notes ./story/. Propose two or three scripts I can review shot by shot.
```

Run the whole production with review points.

```text
Use $mixreel to make the approved script into a finished short.
Stop for my review after the composition drafts, after the keyframes with a video budget,
and before the final cut.
```

The agent records every decision, input and cost in your project folder, so you can stop and resume at any stage.

## What the skill does

**Script from the viewer's experience.** The agent breaks the reference into shots and notes what the viewer expects, learns and feels at each moment. It then looks for scenes in your story that create the same experience, cites where each comes from and marks what was compressed or invented. Every script gets a stranger-viewer check before you see it.

**Scene descriptions you can review.** Each shot is written as one camera setup with visible actions in causal order, a clear ending image and only on-set sound. Risky actions are spelled out as starting state, contact, change and result. You review the picture, not a model prompt.

**Prompts written for each video model.** MiniMax H3 gets a six-part reference prompt bound to the exact upload order of its images. Seedance 2 gets a compact single-setup direction. Neither is converted from the other.

**Keyframes that keep your style and characters.** One composition reference per shot, a simple blocking draft, a finishing pass with your style and character references, then local repairs. GPT only sets up the composition at the start and makes small fixes at the end; Ideogram sets the style and the characters' look. A reference frame that already fits the shot can serve directly as the edit base. Whether it also supplies the style is your choice.

**Cuts timed to what actually happened.** The agent watches the returned clips, finds the real moment of each action and places it on the beat. A local renderer cuts, retimes, adds frame holds and lays the music.

**Spending you can audit.** Quotes, estimates and billed charges stay separate. A paid request is recorded before it is sent and never resubmitted blindly after a timeout.

## Configure your models

Image generation, image editing and video generation can use different services. Create blank private config files outside the repository. The command makes no network calls and imports no keys.

```sh
python3 skills/mixreel/scripts/init_config.py
```

```text
~/.config/mixreel/
├── providers.json      # services, models, endpoints and credential names
└── credentials.json    # your own keys, stored only on this machine
```

See [local configuration](skills/mixreel/references/local-config.md) for how agents read them. The repository ships no paid model client. Your agent uses its own tools or the endpoints you configure, and checks current parameters and pricing first.

## Project structure

```text
skills/mixreel/
  SKILL.md        entry point, stage routing and boundaries
  references/     story, storyboard, images, video and execution rules, read stage by stage
  scripts/        local analysis, edit rendering, plan checks, cost journal, redaction
  assets/         project record template and a synthetic plan example
tests/            automated tests with no paid calls
docs/             design notes and validation record
```

## Tools and checks

Python 3.10 or newer runs the plan checks, journal and redaction tools. Media inspection and edit rendering need `ffmpeg` and `ffprobe`. Beat analysis also needs `numpy` and `librosa`.

```sh
python3 skills/mixreel/scripts/validate_plan.py skills/mixreel/assets/plan.example.json
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

## Contributing

Changes to the creative method should come with observations from a real production and a human review. Keep provider-specific support in its own adapter section, with current documentation and tests that do not trigger paid calls. Keep credentials, signed links and other people's material out of the repository unless you have permission to publish it. [Design notes](docs/DESIGN.md) explain the trade-offs and [validation](docs/VALIDATION.md) separates what has been tested from what has not.

## License

MIT. The license covers the original files of this project. It grants no rights to the reference video, music or character material shown in the showcase.
