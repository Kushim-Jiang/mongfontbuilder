"""Build the fonts this project composes, without running the suites.

    uv run python tests/build.py                  # every font
    uv run python tests/build.py --only unified   # only temp/unified.{ufo,otf}
    uv run python tests/build.py --only hudum     # only temp/hudum.{ufo,otf}

The suites compose the same fonts on the way to shaping them, which is a run of thousands of
cases: this builds them and stops. Nothing here shapes anything, so a change to a drawing or
to a layout of the font is built rather than checked — no case of the suites writes
punctuation, so for one, the conformance run says nothing about the vertical forms of the
marks.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# A Windows console writes what the build prints in its own code page unless it is told
# otherwise.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

from fixtures import buildFontForLocales  # noqa: E402
from mongfontbuilder.data.types import LocaleID  # noqa: E402
from test_unified import buildUnifiedFont  # noqa: E402
from utils import tempDir  # noqa: E402

# The fonts that write with one writing system, by the name of the font. The unified font
# writes with every writing system at once and is composed by `test_unified.py`.
LOCALES: dict[str, list[LocaleID]] = {
    "hudum": ["MNG"],
    "sibe": ["SIB"],
    "manchu": ["MCH"],
}

# The fonts this builds, and the order they are built in.
NAMES = ["unified", *LOCALES]


def build(name: str) -> Path:
    """Build the font *name*, replacing what is in ``temp/``, and answer its path."""

    if name == "unified":
        return buildUnifiedFont()

    # `buildFontForLocales` answers with the font it finds rather than composing it again,
    # and this is the build of the font, so what is there is taken out of the way first.
    for path in (tempDir / f"{name}.otf", tempDir / f"{name}.ufo"):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    return buildFontForLocales(LOCALES[name])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the fonts the suites would compose.")
    parser.add_argument(
        "--only",
        choices=[*NAMES, "all"],
        default="all",
        help="the font to build (default: every font)",
    )
    args = parser.parse_args()

    for name in NAMES if args.only == "all" else [args.only]:
        build(name)


if __name__ == "__main__":
    main()
