"""Write the cases the unified font does not answer as the suites expect.

The conformance run of ``tests/test_unified.py`` says how many cases fail; this says which
ones, and what the font made of each. It shapes every case of the suites against
``temp/unified.otf`` itself, so it needs no pytest log and no run of the suites, and it
writes two reports the work is read from:

- ``temp/unified-failures.txt`` — one block per case, with the letters, the codes, what the
  font made of them and what the suite expects.
- ``temp/unified-failures-compact.txt`` — one line per case, to scan the whole report at once.

Cases the suites expect to be answered differently are marked `xfail` and counted apart from
the failures, so the failures are what is left to fix. Compose the font first, or let this
compose it::

    uv run pytest tests/test_unified.py -s
    uv run python tests/failures.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

# A case is written with the characters of the script, and a Windows console writes them
# in its own code page unless it is told otherwise.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

from test_unified import (  # noqa: E402
    CASES,
    LANGUAGE,
    caseIsXfail,
    caseValues,
    composedOTF,
    composedUFO,
    languageOf,
)
from utils import parseAliases, parseLetter, parseWrittenUnits  # noqa: E402

REPORT = REPO / "temp" / "unified-failures.txt"
COMPACT = REPO / "temp" / "unified-failures-compact.txt"


def composeIfNeeded() -> None:
    """Compose the unified font when one has not been built already."""

    if composedOTF.exists():
        return

    from test_unified import buildUnifiedFont

    buildUnifiedFont()


@dataclass
class Failure:
    """One case the font does not answer as the suite expects."""

    index: str
    locale: str
    letters: str
    goal: str
    codes: str = ""
    result: str = ""
    error: str = field(default="")
    expected: bool = field(default=False)

    @property
    def suite(self) -> str:
        return self.index.split(" > ")[0]

    @property
    def mark(self) -> str:
        return "xfail" if self.expected else "fail"


def collect() -> list[Failure]:
    """Every case that is not answered as expected, or that cannot be read."""

    found = list[Failure]()
    for case in CASES:
        index, letters, locale, goal = caseValues(case)
        expected = caseIsXfail(case)
        try:
            parsed = parseLetter(letters, locale)
            codes = parseAliases(parsed, locale)
            result = parseWrittenUnits(parsed, composedOTF, languageOf(LANGUAGE[locale]))
        except Exception as error:
            message = f"{type(error).__name__}: {error}"
            found.append(Failure(index, locale, letters, goal, error=message, expected=expected))
            continue
        if result != goal:
            found.append(Failure(index, locale, letters, goal, codes, result, expected=expected))
    return found


def report(rows: list[Failure]) -> str:
    """The report of *rows*, counted by suite."""

    lines = list[str]()
    lines.append(f"{len(rows)} of {len(CASES)} cases are not answered as expected")

    suites = dict[str, list[Failure]]()
    for row in rows:
        suites.setdefault(row.suite, []).append(row)
    for suite, rowsOfSuite in suites.items():
        lines.append(f"  {suite}: {len(rowsOfSuite)}")
    lines.append("")

    for row in rows:
        lines.append(f"{row.mark}  {row.index}  locale={row.locale}")
        lines.append(f"  letters: {row.letters}")
        if row.error:
            lines.append(f"  error:   {row.error}")
        else:
            lines.append(f"  codes:   {row.codes}")
            lines.append(f"  result:  {row.result}")
            lines.append(f"  goal:    {row.goal}")
        lines.append("")

    return "\n".join(lines)


def compact(rows: list[Failure]) -> str:
    """One line per case of *rows*, to scan the whole report at once."""

    lines = list[str]()
    for row in rows:
        if row.error:
            lines.append(f"{row.mark:5} > {row.index}  ERROR {row.error}")
        else:
            lines.append(f"{row.mark:5} > {row.index}  res: {row.result}  goal: {row.goal}")
    return "\n".join(lines) + "\n"


def main() -> None:
    composeIfNeeded()
    rows = collect()
    text = report(rows)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(text, encoding="utf-8")
    COMPACT.write_text(compact(rows), encoding="utf-8")
    print(text, flush=True)
    print(f"wrote {REPORT}", flush=True)
    print(f"wrote {COMPACT}", flush=True)
    raise SystemExit(1 if any(not row.expected for row in rows) else 0)


if __name__ == "__main__":
    main()
