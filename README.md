# NarrateFlow Skill

NarrateFlow Skill 将源视频分步骤处理成带旁白的讲解视频。它负责关键帧提取、旁白稿生成、时间轴对齐和视频合成，但不生成语音；MP3 由用户使用自己的工具制作。

## 工作流程

1. 检查 Python、项目依赖、`ffmpeg` 和 `ffprobe`。
2. 在用户项目目录创建 `narrateflow.local.toml` 和 `mp3/`。
3. 从源视频提取关键帧。
4. 询问用户是否有参考文档，再生成并让用户确认旁白稿。
5. 用户生成分段 MP3 并放入项目的 `mp3/` 目录。
6. 校验音频、生成时间轴并合成最终视频。

完整的 Skill 执行规则见 [SKILL.md](SKILL.md)。

## 配置

首次使用时运行：

```bash
python scripts/init_config.py <用户项目目录>
```

然后在生成的 `narrateflow.local.toml` 中填写 `[vlm].base_url` 和 `[vlm].api_key`。配置文件中的 `[keyframes]` 已包含带注释的默认参数，可直接修改关键帧抽取行为。

不要提交或分享包含 API key 的 `narrateflow.local.toml`。

## MP3 要求

- 文件名对应旁白稿段落的 `index`，例如 `p1.mp3`、`p2.mp3`。
- 标题、静音和 `spoken_text` 为空的段落不需要音频。
- 所有 MP3 必须是单声道并使用相同采样率。
- 每个段落只保留一个匹配文件，不要同时放置 `p1.mp3`、`p01.mp3` 和 `p001.mp3`。

## 项目结构

```text
narrateflow-skill/
├── agents/          Skill 界面元数据
├── scripts/         各处理步骤的独立脚本
├── requirements.txt
├── SKILL.md         Codex Skill 执行说明
└── README.md        项目说明
```
