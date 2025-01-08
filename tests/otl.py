from mongfontbuilder.data import locales
from mongfontbuilder.otl import compose


def main() -> None:
    composer = compose(requiredLocales=[*locales.keys()])
    print(composer.asFeatureFile())


if __name__ == "__main__":
    main()
