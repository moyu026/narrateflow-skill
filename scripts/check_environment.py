from __future__ import annotations

import importlib.util
import shutil
import sys


REQUIRED_MODULES = ("cv2", "numpy", "openai", "soundfile")
REQUIRED_COMMANDS = ("ffmpeg", "ffprobe")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    problems: list[str] = []

    if sys.version_info < (3, 11):
        problems.append(f"Python 版本过低：{sys.version.split()[0]}，需要 3.11 或更高版本")

    missing_modules = [
        name for name in REQUIRED_MODULES if importlib.util.find_spec(name) is None
    ]
    if missing_modules:
        problems.append(f"缺少 Python 模块：{', '.join(missing_modules)}")

    missing_commands = [name for name in REQUIRED_COMMANDS if shutil.which(name) is None]
    if missing_commands:
        problems.append(f"缺少系统命令：{', '.join(missing_commands)}")

    if problems:
        print("环境检查未通过：", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print(f"环境检查通过：Python {sys.version.split()[0]}，Python 依赖、ffmpeg 和 ffprobe 均可用。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
