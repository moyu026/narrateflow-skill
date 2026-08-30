from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


KEYFRAME_DEFAULTS = {
    "fps_sample": 1.0,
    "frame_stride": 0,
    "min_gap_sec": 2.0,
    "global_threshold": 12.0,
    "subtitle_threshold": 8.0,
    "detection_max_width": 960,
    "fill_gap_sec": 6.0,
}


def _load_config(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def load_vlm_config(path: Path) -> dict[str, Any]:
    path = path.resolve()
    vlm = _load_config(path).get("vlm", {})
    base_url = str(vlm.get("base_url", "")).strip()
    api_key = str(vlm.get("api_key", "")).strip()
    if not base_url or not api_key:
        raise ValueError(f"请在 {path} 中填写 [vlm].base_url 和 [vlm].api_key")
    return {
        "base_url": base_url,
        "api_key": api_key,
        "provider": str(vlm.get("provider", "openai")),
        "model": str(vlm.get("model", "")).strip() or None,
    }


def load_keyframe_config(path: Path | None = None) -> dict[str, Any]:
    raw = _load_config(path).get("keyframes", {}) if path else {}
    try:
        settings = {
            "fps_sample": float(raw.get("fps_sample", KEYFRAME_DEFAULTS["fps_sample"])),
            "frame_stride": int(raw.get("frame_stride", KEYFRAME_DEFAULTS["frame_stride"])),
            "min_gap_sec": float(raw.get("min_gap_sec", KEYFRAME_DEFAULTS["min_gap_sec"])),
            "global_threshold": float(raw.get("global_threshold", KEYFRAME_DEFAULTS["global_threshold"])),
            "subtitle_threshold": float(raw.get("subtitle_threshold", KEYFRAME_DEFAULTS["subtitle_threshold"])),
            "detection_max_width": int(raw.get("detection_max_width", KEYFRAME_DEFAULTS["detection_max_width"])),
            "fill_gap_sec": float(raw.get("fill_gap_sec", KEYFRAME_DEFAULTS["fill_gap_sec"])),
        }
    except (TypeError, ValueError) as exc:
        raise ValueError("[keyframes] 中包含无效的数字") from exc

    if settings["fps_sample"] <= 0:
        raise ValueError("[keyframes].fps_sample 必须大于 0")
    if settings["frame_stride"] < 0:
        raise ValueError("[keyframes].frame_stride 不能小于 0")
    if settings["min_gap_sec"] < 0:
        raise ValueError("[keyframes].min_gap_sec 不能小于 0")
    if settings["global_threshold"] < 0 or settings["subtitle_threshold"] < 0:
        raise ValueError("[keyframes] 的变化阈值不能小于 0")
    if settings["detection_max_width"] <= 0:
        raise ValueError("[keyframes].detection_max_width 必须大于 0")
    if settings["fill_gap_sec"] <= 0:
        raise ValueError("[keyframes].fill_gap_sec 必须大于 0")

    settings["frame_stride"] = settings["frame_stride"] or None
    return settings
