<h1 align="center">MixReel</h1>

<h3 align="center">Remix any reel into your own story</h3>

<p align="center">A collection of agent skills for reference analysis, scripts, consistent artwork and video production</p>

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

MixReel is a collection of seven skills for Claude Code, Codex and other agents that load skills. Start with a reference video and your advertiser or creative requirements. Ask for a script, a specific production stage, or the full workflow using your chosen assets and services.

Choose which dimensions to borrow, such as a hook, script structure, composition, music, editing or style. Keep those decisions explicit; borrowing one does not automatically copy the others.

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-first-meeting/side-by-side.webp" alt="Reference video on the left, the new short made with this skill on the right" width="608">
</p>
<p align="center"><em>Left, the reference video. Right, a new short made with this skill.</em></p>

## Install

Install the collection together, then invoke each skill independently. Download or clone this repository and run the local installer from the checkout.

```bash
python3 scripts/install_collection.py --destination ~/.codex/skills
```

For a Claude Code project, use `.claude/skills` as the destination. The installer copies all seven skills and shared resources without network access, reading keys or overwriting an existing MixReel installation. For upgrades, install to a fresh directory, inspect it and explicitly replace the previous installation. Do not copy a specialist alone or alter another project's active symlink target.

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

### Point of View

[Reference video](https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/reference.mp4) · [Full short with sound](https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/pov-short.mp4)

A 15.8-second vertical short where the camera is the viewer's eyes. The reference is a game-character fan edit: one close-up per lyric line, her hand reaching into frame, him looking straight into the lens. The new version keeps that first-person feeling with its own characters and setting, in the art style of the official character sheets rather than the reference's look.

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/side-by-side.webp" alt="Reference video on the left, the new short on the right" width="608">
</p>
<p align="center"><em>Left, the reference video. Right, the new short.</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/process.jpg" alt="Composition reference, blocking draft, keyframe and final video for two shots" width="760">
</p>
<p align="center"><em>From composition reference to blocking draft to keyframe to final video, for two of the eight shots. The blocking draft already carries the chosen palette and lighting.</em></p>

<p align="center">
  <img src="https://github.com/LinghuC2333/MixReel/releases/download/showcase-pov/keyframes.jpg" alt="The eight keyframes of the short" width="760">
</p>
<p align="center"><em>All eight keyframes, one per lyric line.</em></p>

The reference videos and the music in both examples belong to their owners and appear here only to demonstrate the workflow.

## Use the skill

Start your agent in a private project folder with the materials relevant to the requested stage. You can invoke `$mixreel-script` directly for an advertising script or `$mixreel-review` for an existing artifact. Other specialist names are listed below.

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

**Scripts grounded in the reference and your goal.** The agent examines the actual opening, reveal and payoff, then chooses what to borrow for your message. Advertising scripts include concrete pictures, exact copy, product behavior and brand/UI treatment. Source-story adaptations cite the material and identify invented scenes. A script-only task needs no generated assets or model account.

**Scene descriptions you can review.** Each shot has a coherent camera behavior, visible actions in causal order and a clear ending image. Risky actions specify starting state, contact, change and result. Keep copy, music, UI and brand requirements in the script and edit plan even when a model prompt excludes them.

**Prompts written for each video model.** MiniMax H3 gets a six-part reference prompt bound to the exact upload order of its images. Seedance 2 gets a compact single-setup direction. Neither is converted from the other.

**Keyframes that keep your style and characters.** Generate only the keyframes needed by the planned sequence, reusing accepted assets and sharing images across shots where sufficient. For each necessary new keyframe, use one composition reference, a simple blocking draft, a finishing pass with your style and character references, then local repairs. GPT only sets up the composition at the start and makes small fixes at the end; Ideogram sets the style and the characters' look. A reference frame that already fits the shot can serve directly as the edit base. Whether it also supplies the style is your choice.

**Connected shots in one generation request.** Plan the sequence before making images. Where the verified endpoint supports it, combine connected shots with a small reference set, the script and supported video/audio inputs. Split for documented capability, scene or rework reasons. Keep fast actions brief within the requested file duration, and compare minimum billing and retry costs per request.

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
