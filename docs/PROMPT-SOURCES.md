# 视频提示词来源与修改

本项目经用户授权，参考其 Lunaverse IDE 中的场景描述与两套视频提示词规则，整理为可独立安装的说明文件。核对日期为 2026 年 10 月 17 日，来源代码版本为 `a37e473fba33516a24184642c370dec5d962d0df`。表中指纹记录实际读取文件的内容，不公开内部项目地址、完整代码或客户故事。

| 来源文件 | 本项目位置 | 来源 SHA-256 |
|---|---|---|
| `agents/asset/skills/seedance-2-cg-video-prompt/SKILL.md` | `references/prompt-seedance-2.md` | `8d2af848df5200d7dedee66b8c8c8eb2410151c3f9996149b86023a92919c2c6` |
| `agents/asset/skills/minimax-h3-cg-video-prompt/SKILL.md` | `references/prompt-minimax-h3.md` | `6cf6db4e4e76569b1a7106d768407d2f95f06ec0f1bae2bef4d21e3e1cbd0581` |
| `agents/asset/skills/minimax-h3-cg-video-prompt/references/h3-ref2va-contract.md` | `references/h3-format.md` | `8b64527da3c88026c0e96d11b6b56ed1c57e3a42c0db178ad3745aed2d2ec740` |
| `agents/asset/skills/minimax-h3-cg-video-prompt/references/cinematic-cg-coverage.md` | `references/cinematic-coverage.md` | `2f0169a964a38be98a2b0995187254dac562284f47a195bcec38dcc653f5d821` |
| `packages/ls-workshop/src/video-cg-description.ts` | `references/storyboard.md` 中的可编辑描述规范 | `c21824c7573f1be66d5ebe57c13f8a68c53220bed1085353617c9b70933d9811` |

## 已做的调整

- 保留 Seedance 2 的简洁场景描述，以及 H3 的六段格式、参考图编号、动作因果、情绪变化和镜头连续性要求。
- H3 直接读取已批准的场景和参考图顺序，不先转换成 Seedance 提示词。模型选定后只读取对应规则。
- 移除 IDE 专用任务命令、固定资料目录和特定小说的校准案例，改由宿主已有工具执行。
- 时长范围、字符限制和模型标识由实际接口核实。来源中的 4 至 15 秒及 4000 字符限制不作为所有接口的默认事实。
- 已批准的镜头与剪辑方案优先，编写模型提示词时不能擅自加入切镜。结束参考图是否强制生效，以接口能力为准。
- 原有服装参考仅在已获准使用时保持。换装任务分别记录人脸与服装来源，防止把身份参考中的衣服带回来。

这些文件迁入的是提示词写法。当前没有附带两家服务的付费调用程序，也未实测它们的现行接口。来源文件保持原样。
