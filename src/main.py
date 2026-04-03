from pprint import pprint

from src.components import (
    create_freileitung,
    create_kabel,
    create_leistungsschalter,
    create_sammelschiene,
    create_trenner,
)
from src.dataset import dataset_1
from src.reliability import (
    analyze_topology_1,
    print_topology_1_analysis,
    print_topology_1_states,
)


def main():
    freileitung_links = create_freileitung(
        "Freileitung links", dataset_1, length_km=20.0
    )
    freileitung_rechts = create_freileitung(
        "Freileitung rechts", dataset_1, length_km=20.0
    )

    kabel_1 = create_kabel("Kabel 1", dataset_1, length_km=10.0)
    kabel_2 = create_kabel("Kabel 2", dataset_1, length_km=10.0)

    sammelschiene_links = create_sammelschiene("Sammelschiene links", dataset_1)
    sammelschiene_rechts = create_sammelschiene("Sammelschiene rechts", dataset_1)

    result = analyze_topology_1(
        freileitung_links=freileitung_links,
        freileitung_rechts=freileitung_rechts,
        kabel_1=kabel_1,
        kabel_2=kabel_2,
        sammelschiene_links=sammelschiene_links,
        sammelschiene_rechts=sammelschiene_rechts,
    )

    print_topology_1_analysis(result)
    print_topology_1_states(result, limit=15)


if __name__ == "__main__":
    main()
