from dataclasses import dataclass
from typing import List

from src.components import Component


@dataclass
class TopologyResult:
    is_available: bool
    available_capacity_fraction: float  # 0.0 ... 1.0
    description: str


# =========================================================
# Hilfsfunktionen
# =========================================================

def is_component_available(component: Component) -> bool:
    """
    Vereinfachtes Modell:
    Komponente gilt als verfügbar, wenn sie nicht im Fehler-/Wartungszustand ist.

    Für den ersten Schritt nehmen wir:
    -> Verfügbarkeit ~ 1 - NV
    -> hier nur boolsche Näherung (später ersetzen!)
    """
    return component.availability > 0.999  # grobe Näherung


# =========================================================
# Topologie 1
# =========================================================

def evaluate_topology_1(
    freileitung_links: Component,
    freileitung_rechts: Component,
    kabel_1: Component,
    kabel_2: Component,
) -> TopologyResult:
    """
    Topologie 1:
    - Zwei parallele Kabel
    - Keine Schaltgeräte in der KÜS
    - Wenn ein Kabel ausfällt → beide betroffen (keine Entkopplung)

    Vereinfachte Logik:
    - Alle Komponenten müssen funktionieren → sonst Totalausfall
    """

    components = [
        freileitung_links,
        freileitung_rechts,
        kabel_1,
        kabel_2,
    ]

    all_available = all(is_component_available(c) for c in components)

    if all_available:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=1.0,
            description="Alle Komponenten verfügbar"
        )
    else:
        return TopologyResult(
            is_available=False,
            available_capacity_fraction=0.0,
            description="Mindestens eine Komponente ausgefallen"
        )


# =========================================================
# Topologie 2
# =========================================================

def evaluate_topology_2(
    freileitung_links: Component,
    freileitung_rechts: Component,
    kabel_1: Component,
    kabel_2: Component,
    leistungsschalter: Component,
    trenner: Component,
    sammelschiene: Component,
) -> TopologyResult:
    """
    Topologie 2:
    - Zwei getrennte Kabelsysteme
    - Schaltanlage vorhanden
    - Teilbetrieb möglich

    Logik:
    - Freileitungen + Schaltanlage müssen funktionieren
    - Kabel können teilweise ausfallen → reduzierte Kapazität
    """

    # zentrale Komponenten
    core_components = [
        freileitung_links,
        freileitung_rechts,
        leistungsschalter,
        trenner,
        sammelschiene,
    ]

    core_ok = all(is_component_available(c) for c in core_components)

    if not core_ok:
        return TopologyResult(
            is_available=False,
            available_capacity_fraction=0.0,
            description="Zentrale Komponente ausgefallen"
        )

    # Kabel prüfen
    kabel_1_ok = is_component_available(kabel_1)
    kabel_2_ok = is_component_available(kabel_2)

    if kabel_1_ok and kabel_2_ok:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=1.0,
            description="Beide Kabel verfügbar"
        )

    elif kabel_1_ok or kabel_2_ok:
        return TopologyResult(
            is_available=True,
            available_capacity_fraction=0.5,
            description="Ein Kabel verfügbar"
        )

    else:
        return TopologyResult(
            is_available=False,
            available_capacity_fraction=0.0,
            description="Beide Kabel ausgefallen"
        )


# =========================================================
# Wrapper (optional)
# =========================================================

def evaluate_topology(name: str, *args) -> TopologyResult:
    if name == "topology_1":
        return evaluate_topology_1(*args)
    elif name == "topology_2":
        return evaluate_topology_2(*args)
    else:
        raise ValueError(f"Unbekannte Topologie: {name}")
