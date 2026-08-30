from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import soundfile as sf


def _audio_path(audio_dir: Path, paragraph_index: int) -> Path:
    candidates = {
        audio_dir / f"p{paragraph_index}.mp3",
        audio_dir / f"p{paragraph_index:02d}.mp3",
        audio_dir / f"p{paragraph_index:03d}.mp3",
    }
    matches = sorted(path for path in candidates if path.is_file())
    if len(matches) != 1:
        names = ", ".join(path.name for path in sorted(candidates))
        raise FileNotFoundError(
            f"段落 {paragraph_index} 必须且只能匹配一个音频文件: {names}"
        )
    return matches[0].resolve()


def build_audio_manifest(spoken_json: Path, audio_dir: Path, output: Path) -> Path:
    payload = json.loads(spoken_json.read_text(encoding="utf-8"))
    paragraphs = [
        item
        for item in payload.get("paragraphs", [])
        if not item.get("is_title")
        and not item.get("is_silent")
        and str(item.get("spoken_text", "")).strip()
    ]
    if not paragraphs:
        raise ValueError("旁白稿中没有可用的非标题段落")

    sample_rate: int | None = None
    cursor = 0.0
    segments: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        paragraph_index = int(paragraph["index"])
        audio_path = _audio_path(audio_dir, paragraph_index)
        info = sf.info(audio_path)
        if info.channels != 1:
            raise ValueError(f"MP3 音频必须是单声道: {audio_path}")
        if sample_rate is None:
            sample_rate = info.samplerate
        elif info.samplerate != sample_rate:
            raise ValueError(f"所有音频必须使用相同采样率: {audio_path}")
        segments.append(
            {
                "paragraph_index": paragraph_index,
                "segment_id": f"p{paragraph_index}",
                "source_text": str(paragraph.get("source_text", "")),
                "spoken_text": str(paragraph.get("spoken_text", "")),
                "audio_path": str(audio_path),
                "start": round(cursor, 3),
                "end": round(cursor + info.duration, 3),
                "duration": round(info.duration, 3),
            }
        )
        cursor += info.duration

    result = {
        "page": int(payload.get("page", 1)),
        "title_text": payload.get("title_text", ""),
        "sample_rate": sample_rate,
        "segments": segments,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="为用户提供的分段 MP3 音频生成清单")
    parser.add_argument("--spoken-json", required=True)
    parser.add_argument("--audio-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = build_audio_manifest(Path(args.spoken_json), Path(args.audio_dir), Path(args.output))
    print(output.resolve())


if __name__ == "__main__":
    main()
