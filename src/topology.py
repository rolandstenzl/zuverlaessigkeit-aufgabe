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
    - konservatives Anfangsmodell:
      sobald eine Komponente nicht 'up' ist -> Totalausfall
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
    kabel_1_state: str,
    kabel_2_state: str,
    leistungsschalter_state: str,
    trenner_state: str,
    sammelschiene_state: str,
) -> TopologyResult:
    """
    Topologie 2:
    - getrennte Kabelsysteme
    - Schaltanlage vorhanden
    - Teilbetrieb bei Ausfall eines Kabels möglich
    """

    core_states = [
        freileitung_links_state,
        freileitung_rechts_state,
        leistungsschalter_state,
        trenner_state,
        sammelschiene_state,
    ]

    if not all(is_up(s) for s in core_states):
        return TopologyResult(
            is_available=False,
            available_capacity_fraction=0.0,
            description="Zentrale Komponente nicht verfügbar",
        )

    kabel_1_up = is_up(kabel_1_state)
    kabel_2_up = is_up(kabel_2_state)

    if kabel_1_up and kabel_2_up:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=1.0,
            description="Beide Kabel in Betrieb",
        )

    if kabel_1_up or kabel_2_up:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=0.5,
            description="Ein Kabel in Betrieb",
        )

    return TopologyResult(
        is_available=False,
        available_capacity_fraction=0.0,
        description="Kein Kabel in Betrieb",
    )


def evaluate_topology(name: str, *args) -> TopologyResult:
    if name == "topology_1":
        return evaluate_topology_1(*args)
    elif name == "topology_2":
        return evaluate_topology_2(*args)
    else:
        raise ValueError(f"Unbekannte Topologie: {name}")
