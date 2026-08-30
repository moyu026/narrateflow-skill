---
name: narrateflow-skill
description: 分步骤把源视频处理为带外部旁白音频的讲解视频。适用于抽取关键帧、生成旁白稿、导入用户提供的 MP3、对齐时间轴或合成成片；本技能不生成语音。
---

# NarrateFlow Skill

本技能不是需要整体启动的应用。根据任务进度，直接调用 `scripts/` 中对应的独立脚本。所有输出都写入用户项目目录，不要写入技能安装目录。

## 步骤 1：验证并配置运行环境

每次开始使用本技能时，先检查 `uv`：

```text
uv --version
```

如果命令不可用，使用当前操作系统的软件包管理器安装 `uv`。安装完成后运行：

```text
uv run --python 3.13 --no-project --with-requirements <技能目录>/requirements.txt python <技能目录>/scripts/check_environment.py
```

该命令会准备 Python 3.13 和 `requirements.txt` 中的依赖，并检查 `ffmpeg`、`ffprobe`。如果检查失败，使用当前操作系统的软件包管理器安装报告中缺少的系统命令，然后重复检查。只有看到“环境检查通过”后才能继续；已满足要求时不要重复安装或修改环境。

## 步骤 2：创建项目配置

处理任何视频前，运行：

```text
python <技能目录>/scripts/init_config.py <用户项目目录>
```

脚本同时创建 `<用户项目目录>/mp3/`，用于接收用户提供的分段音频。如果脚本创建了 `narrateflow.local.toml`，或提示凭据不完整，立即暂停。告诉用户配置文件的绝对路径，请用户自行填写 `[vlm].base_url` 和 `[vlm].api_key`。配置文件同时包含带注释的 `[keyframes]` 默认参数，用户可以按需修改；然后再次调用本技能。

不要让用户在对话中提供 API key，不要读取、输出或回显 API key。

## 后续脚本的运行方式

执行步骤脚本时，优先使用技能自带的依赖清单：

```text
uv run --python 3.13 --no-project --with-requirements <技能目录>/requirements.txt python <脚本> <参数>
```

## 步骤 3：抽取关键帧

调用 `scripts/extract_keyframes.py`：

```text
--video <源视频>
--output <项目目录>/outputs/keyframes.json
--config <项目目录>/narrateflow.local.toml
```

脚本读取配置文件中的 `[keyframes]` 参数。`--fps-sample`、`--frame-stride`、`--min-gap-sec`、`--global-threshold`、`--subtitle-threshold`、`--detection-max-width` 和 `--fill-gap-sec` 可用于单次覆盖配置值。输出 `keyframes.json` 和同目录下的 `keyframes/` 图片。用户只要求重新分析画面时，可以单独运行本步骤。

## 步骤 4：生成旁白稿

运行脚本前，必须先询问用户是否有参考文档。用户尚未回答时暂停，不要直接生成旁白稿；如果当前对话中用户已经提供文档或明确表示没有，则不必重复询问。

- 用户没有参考文档：省略 `--reference-text`。
- 用户提供参考文档：提取其中与视频讲解有关的文字，保存为 UTF-8 文本文件，并通过 `--reference-text <参考文本文件>` 传入。不要改写参考内容后再交给脚本。

调用 `scripts/generate_narration.py`：

```text
--video <源视频>
--keyframes <keyframes.json>
--output-dir <项目目录>/outputs/scripts
--debug-dir <项目目录>/outputs/debug
--config <项目目录>/narrateflow.local.toml
```

其他可选参数为 `--cover-image`、`--cover-duration-sec` 和 `--batch-size`。输出为 `page_01.spoken.json`。

生成后必须暂停，让用户检查并按需修改 `paragraphs[].spoken_text`。告诉用户 `<项目目录>/mp3/` 的绝对路径，请用户使用自己的语音工具为每个非标题、非静音且 `spoken_text` 非空的段落生成单声道 MP3，并把文件放入该目录。文件名使用段落 `index`，例如 `p1.mp3`、`p2.mp3`；所有文件必须使用相同采样率，每个段落只能有一个匹配文件。

本技能不得调用 TTS、生成占位音频或跳过缺失音频。

## 步骤 5：建立音频清单

用户提供完 MP3 后，调用 `scripts/build_audio_manifest.py`：

```text
--spoken-json <page_01.spoken.json>
--audio-dir <项目目录>/mp3
--output <项目目录>/outputs/segments_manifest.json
```

脚本会校验段落完整性、单声道和统一采样率。校验失败时停止，不要继续合成。

## 步骤 6：生成时间轴

调用 `scripts/align_timeline.py`：

```text
--video <源视频>
--spoken-json <page_01.spoken.json>
--output <项目目录>/outputs/timeline.json
--debug-dir <项目目录>/outputs/timeline-debug
--config <项目目录>/narrateflow.local.toml
```

输出中缺少段落或状态不是 `complete` 时，先让用户检查时间轴，不要直接合成。

## 步骤 7：合成视频

调用 `scripts/compose_video.py`：

```text
--video <源视频>
--timeline <timeline.json>
--segments-manifest <segments_manifest.json>
--output-dir <项目目录>/outputs/composed
```

可选封面参数为 `--cover-image`、`--cover-duration-sec`、`--cover-paragraph-index`；可选片尾参数为 `--outro-image`、`--outro-audio`。启用片尾时必须同时提供图片和音频，且片尾音频的采样率必须与段落 MP3 一致。

合成器按照时间轴放置用户音频。当旁白需要更多时间时，调整对应视频片段速度而不截断音频。完成后向用户报告 `page_composed.mp4` 的绝对路径。

## 按需运行

如果用户已有某一步的有效输出，从下一步继续，不要重复前面的步骤。每个脚本只负责自己的输入和输出；不要重新引入总控脚本、运行模式或完整项目配置。
