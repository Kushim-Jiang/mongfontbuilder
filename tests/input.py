import sys
from pathlib import Path

from utils import parse_code, parse_glyphs


def main() -> None:
    _, font, writingSystem = sys.argv

    while True:
        text = input("input: ")
        print(parse_code(text, writingSystem))
        print(parse_glyphs(text, Path(font)))


if __name__ == "__main__":
    main()
