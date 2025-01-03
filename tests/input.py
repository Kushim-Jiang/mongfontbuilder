import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / ".."))
from tests import parse_code, parse_glyphs


def main() -> None:
    _, writingSystem = sys.argv

    while True:
        text = input("input: ")
        print(parse_code(text, writingSystem))
        print(parse_glyphs(text))


if __name__ == "__main__":
    main()
