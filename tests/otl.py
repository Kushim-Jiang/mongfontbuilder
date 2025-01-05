from mongfontbuilder.data import locales
from mongfontbuilder.otl import compose


def main() -> None:
    composer = compose(locales=[*locales.keys()])
    print(composer.code())


if __name__ == "__main__":
    main()
