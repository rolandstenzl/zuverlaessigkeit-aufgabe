import os
import sys

from src.components import create_freileitung, create_kabel, create_sammelschiene
from src.dataset import dataset_1, dataset_2, dataset_3
from src.reliability import (
    analyze_topology_1,
    analyze_topology_2,
    print_topology_1_analysis,
    print_topology_1_states,
    print_topology_2_analysis,
    print_topology_2_states,
)


def run_topology_1_for_dataset(dataset):
    print("\n" + "#" * 90)
    print(f"Auswertung für: {dataset.name}")
    print("#" * 90)

    # Komponenten erzeugen
    freileitung_links = create_freileitung("Freileitung links", dataset, length_km=20.0)
    freileitung_rechts = create_freileitung(
        "Freileitung rechts", dataset, length_km=20.0
    )

    kabel_1 = create_kabel("Kabel 1", dataset, length_km=10.0)
    kabel_2 = create_kabel("Kabel 2", dataset, length_km=10.0)

    sammelschiene_links = create_sammelschiene("Sammelschiene links", dataset)
    sammelschiene_rechts = create_sammelschiene("Sammelschiene rechts", dataset)

    # Analyse
    result = analyze_topology_1(
        freileitung_links=freileitung_links,
        freileitung_rechts=freileitung_rechts,
        kabel_1=kabel_1,
        kabel_2=kabel_2,
        sammelschiene_links=sammelschiene_links,
        sammelschiene_rechts=sammelschiene_rechts,
    )

    # Ausgabe
    print_topology_1_analysis(result)
    print_topology_1_states(result, limit=10)


def run_topology_2_for_dataset(dataset):
    print("\n" + "#" * 90)
    print(f"Auswertung für: {dataset.name} (Topologie 2)")
    print("#" * 90)

    # -------------------------------------------------
    # Basis-Komponenten
    # -------------------------------------------------
    freileitung_links = create_freileitung("Freileitung links", dataset, length_km=20.0)
    freileitung_rechts = create_freileitung(
        "Freileitung rechts", dataset, length_km=20.0
    )

    kabel_1 = create_kabel("Kabel 1", dataset, length_km=10.0)
    kabel_2 = create_kabel("Kabel 2", dataset, length_km=10.0)

    # -------------------------------------------------
    # Gemeinsame Schaltfelder
    # -------------------------------------------------
    schaltfeld_links = create_sammelschiene("Schaltfeld links", dataset)
    schaltfeld_rechts = create_sammelschiene("Schaltfeld rechts", dataset)

    # -------------------------------------------------
    # Sammelschienen links / rechts
    # -------------------------------------------------
    sammelschiene_links = create_sammelschiene("Sammelschiene links", dataset)
    sammelschiene_rechts = create_sammelschiene("Sammelschiene rechts", dataset)

    # -------------------------------------------------
    # Kabelzweig 1
    # -------------------------------------------------
    schaltfeld_kabel_1_links = create_sammelschiene("Schaltfeld Kabel 1 links", dataset)
    schaltfeld_kabel_1_rechts = create_sammelschiene(
        "Schaltfeld Kabel 1 rechts", dataset
    )

    # -------------------------------------------------
    # Kabelzweig 2
    # -------------------------------------------------
    schaltfeld_kabel_2_links = create_sammelschiene("Schaltfeld Kabel 2 links", dataset)
    schaltfeld_kabel_2_rechts = create_sammelschiene(
        "Schaltfeld Kabel 2 rechts", dataset
    )

    # -------------------------------------------------
    # Analyse
    # -------------------------------------------------
    result = analyze_topology_2(
        freileitung_links=freileitung_links,
        freileitung_rechts=freileitung_rechts,
        schaltfeld_links=schaltfeld_links,
        schaltfeld_rechts=schaltfeld_rechts,
        sammelschiene_links=sammelschiene_links,
        sammelschiene_rechts=sammelschiene_rechts,
        kabel_1=kabel_1,
        kabel_2=kabel_2,
        schaltfeld_kabel_1_links=schaltfeld_kabel_1_links,
        schaltfeld_kabel_1_rechts=schaltfeld_kabel_1_rechts,
        schaltfeld_kabel_2_links=schaltfeld_kabel_2_links,
        schaltfeld_kabel_2_rechts=schaltfeld_kabel_2_rechts,
    )

    # -------------------------------------------------
    # Ausgabe
    # -------------------------------------------------
    print_topology_2_analysis(result)
    print_topology_2_states(result, limit=10)


def main():
    datasets = [dataset_1, dataset_2, dataset_3]

    # -------------------------------------------------
    # results Ordner anlegen
    # -------------------------------------------------
    os.makedirs("results", exist_ok=True)

    output_file_path = "results/analysis.txt"

    # -------------------------------------------------
    # Ausgabe umleiten (print → Datei)
    # -------------------------------------------------
    original_stdout = sys.stdout

    with open(output_file_path, "w") as f:
        sys.stdout = f

        for dataset in datasets:
            run_topology_1_for_dataset(dataset)
            run_topology_2_for_dataset(dataset)

        # wieder zurücksetzen
        sys.stdout = original_stdout

    print(f"Ergebnisse wurden gespeichert in: {output_file_path}")


if __name__ == "__main__":
    main()
