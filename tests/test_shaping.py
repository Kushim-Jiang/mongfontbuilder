from utils import core_test, eac_test, parse_code


def test_core():
    for writing_system in core_test.writing_systems:
        core_test.core_test(writing_system)


def test_input(writing_system: str):
    while True:
        chars = input("input: ")
        print(parse_code(chars, writing_system))
        print(eac_test.parse_glyphs(chars))


def test_eac(writing_system: str):
    eac_test.eac_test(writing_system)


if __name__ == "__main__":
    test_core()
