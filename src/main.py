from pprint import pprint

from src.datasets import dataset_1
from src.components import (
    create_freileitung,
    create_kabel,
    create_trenner,
    create_leistungsschalter,
    create_sammelschiene,
)


def main():
    freileitung_links = create_freileitung("Freileitung links", dataset_1, length_km=20.0)
    freileitung_rechts = create_freileitung("Freileitung rechts", dataset_1, length_km=20.0)
    kabel = create_kabel("Kabel", dataset_1, length_km=10.0)

    trenner = create_trenner("Trenner KÜS", dataset_1)
    leistungsschalter = create_leistungsschalter("Leistungsschalter KÜS", dataset_1)
    sammelschiene = create_sammelschiene("Sammelschiene KÜS", dataset_1)

    components = [
        freileitung_links,
        freileitung_rechts,
        kabel,
        trenner,
        leistungsschalter,
        sammelschiene,
    ]

    for component in components:
        print("\n" + "=" * 60)
        pprint(component.summary_dict())


if __name__ == "__main__":
    main()
