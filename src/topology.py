from dataclasses import dataclass


@dataclass
class TopologyResult:
    is_available: bool
    available_capacity_fraction: float
    description: str


def is_up(state: str) -> bool:
    return state == "up"


# =========================================================
# Topologie 1
# =========================================================


def evaluate_topology_1(
    freileitung_links_state: str,
    freileitung_rechts_state: str,
    kabel_1_state: str,
    kabel_2_state: str,
    sammelschiene_links_state: str,
    sammelschiene_rechts_state: str,
) -> TopologyResult:
    """
    Topologie 1:
    - Doppelkabel ohne Schaltgeräte
    - keine selektive Abschaltung einzelner Systeme
    - Modell: Ausfall einer Komponente -> Totalausfall
    """

    states = [
        freileitung_links_state,
        freileitung_rechts_state,
        kabel_1_state,
        kabel_2_state,
        sammelschiene_links_state,
        sammelschiene_rechts_state,
    ]

    if all(is_up(s) for s in states):
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=1.0,
            description="Alle Komponenten in Betrieb",
        )

    return TopologyResult(
        is_available=False,
        available_capacity_fraction=0.0,
        description="Mindestens eine Komponente nicht verfügbar",
    )


# =========================================================
# Topologie 2
# =========================================================


def evaluate_topology_2(
    freileitung_links_state: str,
    freileitung_rechts_state: str,
    schaltfeld_links_state: str,
    schaltfeld_rechts_state: str,
    sammelschiene_links_state: str,
    sammelschiene_rechts_state: str,
    kabel_1_state: str,
    kabel_2_state: str,
    schaltfeld_kabel_1_links_state: str,
    schaltfeld_kabel_1_rechts_state: str,
    schaltfeld_kabel_2_links_state: str,
    schaltfeld_kabel_2_rechts_state: str,
) -> TopologyResult:
    """
    Topologie 2:

    Freileitung links
    -> Schaltfeld links
    -> Sammelschiene links
    -> Parallel:
         Zweig 1: Schaltfeld K1 links - Kabel 1 - Schaltfeld K1 rechts
         Zweig 2: Schaltfeld K2 links - Kabel 2 - Schaltfeld K2 rechts
    -> Sammelschiene rechts
    -> Schaltfeld rechts
    -> Freileitung rechts

    Aufbau:
    - Alles vor der Verzweigung und nach der Zusammenführung liegt in Serie
    - Die beiden Kabelzweige liegen parallel
    - Fällt ein Zweig aus, bleibt 50 % Kapazität
    - Fallen beide aus, 0 %
    """

    # -----------------------------------------------------
    # Gemeinsamer Serienpfad
    # -----------------------------------------------------

    # Sind alle seriellen Bauteile up?
    common_ok = all(
        [
            is_up(freileitung_links_state),
            is_up(schaltfeld_links_state),
            is_up(sammelschiene_links_state),
            is_up(sammelschiene_rechts_state),
            is_up(schaltfeld_rechts_state),
            is_up(freileitung_rechts_state),
        ]
    )

    if not common_ok:
        return TopologyResult(
            is_available=False,
            available_capacity_fraction=0.0,
            description="Gemeinsamer Pfad nicht verfügbar",
        )

    # -----------------------------------------------------
    # Zweig 1
    # -----------------------------------------------------
    branch_1_ok = all(
        [
            is_up(schaltfeld_kabel_1_links_state),
            is_up(kabel_1_state),
            is_up(schaltfeld_kabel_1_rechts_state),
        ]
    )

    # -----------------------------------------------------
    # Zweig 2
    # -----------------------------------------------------
    branch_2_ok = all(
        [
            is_up(schaltfeld_kabel_2_links_state),
            is_up(kabel_2_state),
            is_up(schaltfeld_kabel_2_rechts_state),
        ]
    )

    # -----------------------------------------------------
    # Parallelstruktur
    # -----------------------------------------------------
    if branch_1_ok and branch_2_ok:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=1.0,
            description="Beide Kabelzweige verfügbar",
        )

    if branch_1_ok or branch_2_ok:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=0.5,
            description="Ein Kabelzweig verfügbar",
        )

    return TopologyResult(
        is_available=False,
        available_capacity_fraction=0.0,
        description="Kein Kabelzweig verfügbar",
    )


def evaluate_topology(name: str, *args) -> TopologyResult:
    if name == "topology_1":
        return evaluate_topology_1(*args)
    elif name == "topology_2":
        return evaluate_topology_2(*args)
    else:
        raise ValueError(f"Unbekannte Topologie: {name}")
