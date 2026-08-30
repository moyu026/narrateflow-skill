from __future__ import annotations

import sys
import tomllib
from pathlib import Path


CONFIG_NAME = "narrateflow.local.toml"
MP3_DIR_NAME = "mp3"
CONFIG_TEMPLATE = """[vlm]
# OpenAI 兼容接口地址，例如 https://example.com/v1
base_url = ''
# 接口密钥；请只在本地配置文件中填写
api_key = ''
# 接口类型，目前使用 OpenAI 兼容格式
provider = 'openai'
# 模型名称；留空时由接口使用默认模型
model = ''

[keyframes]
# 每秒检测多少帧；frame_stride 大于 0 时本参数不生效
fps_sample = 1.0
# 固定每隔多少帧检测一次；0 表示根据 fps_sample 自动计算
frame_stride = 0
# 两个画面变化关键帧之间的最短间隔，单位为秒
min_gap_sec = 2.0
# 整体画面变化阈值；越小越容易保留关键帧
global_threshold = 12.0
# 文字区域变化阈值；越小越容易捕获字幕或页面文字变化
subtitle_threshold = 8.0
# 检测时缩放画面的最大宽度；降低可加快检测
detection_max_width = 960
# 长时间无变化时补充关键帧的间隔，单位为秒
fill_gap_sec = 6.0
"""


def main() -> int:
    project_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not project_dir.is_dir():
        print(f"Project directory does not exist: {project_dir}", file=sys.stderr)
        return 1

    config_path = project_dir / CONFIG_NAME
    if not config_path.exists():
        config_path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
        print(f"Created {config_path}")

    mp3_dir = project_dir / MP3_DIR_NAME
    mp3_dir.mkdir(exist_ok=True)

    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"Invalid config {config_path}: {exc}", file=sys.stderr)
        return 1

    vlm = payload.get("vlm", {})
    missing = [name for name in ("base_url", "api_key") if not str(vlm.get(name, "")).strip()]
    if missing:
        print(f"Fill [vlm].base_url and [vlm].api_key in {config_path}")
        return 2

    print(f"Config ready: {config_path}")
    print(f"MP3 directory ready: {mp3_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
