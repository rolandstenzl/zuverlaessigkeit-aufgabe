from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Tuple

from src.components import Component
from src.topology import TopologyResult, evaluate_topology_1

# =========================================================
# Datenklassen für Ergebnisse
# =========================================================


@dataclass
class StateEvaluation:
    state: Dict[str, str]
    probability: float
    topology_result: TopologyResult


@dataclass
class Topology1AnalysisResult:
    state_evaluations: List[StateEvaluation]
    capacity_probabilities: Dict[float, float]
    non_availability: float


# =========================================================
# Zustandswahrscheinlichkeiten einzelner Komponenten
# =========================================================


def get_component_state_probabilities(component: Component) -> Dict[str, float]:
    """
    Liefert die Zustandswahrscheinlichkeiten einer einzelnen Komponente.

    Für Komponenten ohne Wartung:
        - up
        - failed

    Für Komponenten mit Wartung:
        - up
        - failed
        - maintenance

    Annahme:
    NV_total = NV_failure + NV_maintenance
    """
    p_failed = component.nv_failure
    p_maintenance = component.nv_maintenance
    p_up = 1.0 - p_failed - p_maintenance

    # kleine numerische Sicherung
    if p_up < 0:
        raise ValueError(
            f"Negative Up-Wahrscheinlichkeit bei Komponente {component.name}: {p_up}"
        )

    state_probs = {
        "up": p_up,
        "failed": p_failed,
    }

    if p_maintenance > 0:
        state_probs["maintenance"] = p_maintenance

    return state_probs


# =========================================================
# Hilfsfunktionen für Topologie 1
# =========================================================


def is_valid_topology_1_state(state: Dict[str, str]) -> bool:
    """
    Filtert unzulässige Zustände.

    Laut Aufgabenstellung:
    - nur ein Kabel gleichzeitig in Wartung
    """
    kabel_1_maintenance = state["kabel_1"] == "maintenance"
    kabel_2_maintenance = state["kabel_2"] == "maintenance"

    if kabel_1_maintenance and kabel_2_maintenance:
        return False

    return True


def compute_state_probability(
    state: Dict[str, str],
    component_state_probabilities: Dict[str, Dict[str, float]],
) -> float:
    """
    Multipliziert die Einzelwahrscheinlichkeiten zum Gesamtzustand.
    """
    probability = 1.0
    for component_name, component_state in state.items():
        probability *= component_state_probabilities[component_name][component_state]
    return probability


# =========================================================
# Analyse Topologie 1
# =========================================================


def analyze_topology_1(
    freileitung_links: Component,
    freileitung_rechts: Component,
    kabel_1: Component,
    kabel_2: Component,
    sammelschiene_links: Component,
    sammelschiene_rechts: Component,
) -> Topology1AnalysisResult:
    """
    Analysiert Topologie 1 über vollständige Zustandsenumeration.

    Komponenten:
    - Freileitung links
    - Freileitung rechts
    - Kabel 1
    - Kabel 2
    - Sammelschiene links
    - Sammelschiene rechts

    Ergebnis:
    - Wahrscheinlichkeit jeder Kapazitätsstufe
    - Nicht-Verfügbarkeit der Übertragungsstrecke
    """

    components = {
        "freileitung_links": freileitung_links,
        "freileitung_rechts": freileitung_rechts,
        "kabel_1": kabel_1,
        "kabel_2": kabel_2,
        "sammelschiene_links": sammelschiene_links,
        "sammelschiene_rechts": sammelschiene_rechts,
    }

    component_state_probabilities = {
        name: get_component_state_probabilities(component)
        for name, component in components.items()
    }

    component_state_lists = {
        name: list(state_probs.keys())
        for name, state_probs in component_state_probabilities.items()
    }

    state_evaluations: List[StateEvaluation] = []
    capacity_probabilities: Dict[float, float] = {}

    total_generated_states = 0
    valid_states = 0
    skipped_states = 0

    all_state_combinations = product(
        component_state_lists["freileitung_links"],
        component_state_lists["freileitung_rechts"],
        component_state_lists["kabel_1"],
        component_state_lists["kabel_2"],
        component_state_lists["sammelschiene_links"],
        component_state_lists["sammelschiene_rechts"],
    )

    for (
        freileitung_links_state,
        freileitung_rechts_state,
        kabel_1_state,
        kabel_2_state,
        sammelschiene_links_state,
        sammelschiene_rechts_state,
    ) in all_state_combinations:
        total_generated_states += 1

        state = {
            "freileitung_links": freileitung_links_state,
            "freileitung_rechts": freileitung_rechts_state,
            "kabel_1": kabel_1_state,
            "kabel_2": kabel_2_state,
            "sammelschiene_links": sammelschiene_links_state,
            "sammelschiene_rechts": sammelschiene_rechts_state,
        }

        if not is_valid_topology_1_state(state):
            skipped_states += 1
            continue

        valid_states += 1

        probability = compute_state_probability(state, component_state_probabilities)

        topology_result = evaluate_topology_1(
            freileitung_links_state=state["freileitung_links"],
            freileitung_rechts_state=state["freileitung_rechts"],
            kabel_1_state=state["kabel_1"],
            kabel_2_state=state["kabel_2"],
            sammelschiene_links_state=state["sammelschiene_links"],
            sammelschiene_rechts_state=state["sammelschiene_rechts"],
        )

        state_evaluations.append(
            StateEvaluation(
                state=state,
                probability=probability,
                topology_result=topology_result,
            )
        )

        capacity = topology_result.available_capacity_fraction
        capacity_probabilities[capacity] = (
            capacity_probabilities.get(capacity, 0.0) + probability
        )

    non_availability = capacity_probabilities.get(0.0, 0.0)

    total_probability = sum(capacity_probabilities.values())
    if total_probability <= 0.0:
        raise ValueError(
            "Keine gültigen Zustände mit positiver Wahrscheinlichkeit berechnet."
        )

    # kleine numerische Plausibilitätsprüfung
    if total_probability > 1.000001:
        raise ValueError(
            f"Summe der Zustandswahrscheinlichkeiten > 1: {total_probability:.8f}"
        )

    # Optional: normieren, falls durch Rundung minimal < 1
    # Für den Moment lassen wir die Originalwerte bewusst unverändert.

    return Topology1AnalysisResult(
        state_evaluations=state_evaluations,
        capacity_probabilities=capacity_probabilities,
        non_availability=non_availability,
    )


# =========================================================
# Ausgabehilfen
# =========================================================


def print_topology_1_analysis(result: Topology1AnalysisResult) -> None:
    print("\n" + "=" * 90)
    print("Analyseergebnis Topologie 1")
    print("=" * 90)

    # ---------------------------------------------------------
    # Kapazitätsverteilung
    # ---------------------------------------------------------
    print("\nWahrscheinlichkeit je Kapazitätsstufe:")

    for capacity in sorted(result.capacity_probabilities.keys(), reverse=True):
        probability = result.capacity_probabilities[capacity]
        print(f"  Kapazität {capacity:>4.1f} : {probability:.8f}")

    # ---------------------------------------------------------
    # Explizite Hauptkennwerte
    # ---------------------------------------------------------
    p_full = result.capacity_probabilities.get(1.0, 0.0)
    p_half = result.capacity_probabilities.get(0.5, 0.0)
    p_zero = result.capacity_probabilities.get(0.0, 0.0)

    print("\n" + "-" * 90)
    print("Zusammenfassung:")

    print(f"  P(100% Kapazität) : {p_full:.8f}")
    print(f"  P( 50% Kapazität) : {p_half:.8f}")
    print(f"  P(  0% Kapazität) : {p_zero:.8f}")

    # ---------------------------------------------------------
    # Verfügbarkeit / Nicht-Verfügbarkeit
    # ---------------------------------------------------------
    print("\n" + "-" * 90)

    print(f"Nicht-Verfügbarkeit der Übertragungsstrecke: {result.non_availability:.8f}")

    availability = 1.0 - result.non_availability
    print(f"Verfügbarkeit der Übertragungsstrecke:     {availability:.8f}")

    # ---------------------------------------------------------
    # Plausibilitätscheck
    # ---------------------------------------------------------
    print("\n" + "-" * 90)

    total_probability = sum(result.capacity_probabilities.values())

    print(f"Summe der Zustandswahrscheinlichkeiten:     {total_probability:.8f}")

    # kleiner numerischer Check
    if abs(total_probability - 1.0) > 1e-6:
        print("⚠️ WARNUNG: Wahrscheinlichkeiten summieren sich nicht zu 1!")
    else:
        print("✔ Wahrscheinlichkeiten konsistent (≈ 1.0)")

    print("=" * 90)


def print_topology_1_states(result: Topology1AnalysisResult, limit: int = 20) -> None:
    """
    Gibt die ersten Zustände zur Kontrolle aus.
    """
    print("\n" + "=" * 90)
    print(f"Erste {limit} Zustände Topologie 1")
    print("=" * 90)

    for i, evaluation in enumerate(result.state_evaluations[:limit], start=1):
        state = evaluation.state
        print(
            f"{i:>2d}. "
            f"FL links={state['freileitung_links']}, "
            f"SS links={state['sammelschiene_links']}, "
            f"K1={state['kabel_1']}, "
            f"K2={state['kabel_2']}, "
            f"SS rechts={state['sammelschiene_rechts']}, "
            f"FL rechts={state['freileitung_rechts']} | "
            f"P={evaluation.probability:.8f} | "
            f"Kapazität={evaluation.topology_result.available_capacity_fraction:.1f} | "
            f"{evaluation.topology_result.description}"
        )


# =========================================================
# Analyse Topologie 2
# =========================================================

from src.topology import evaluate_topology_2


@dataclass
class Topology2AnalysisResult:
    state_evaluations: List[StateEvaluation]
    capacity_probabilities: Dict[float, float]
    non_availability: float


def is_valid_topology_2_state(state: Dict[str, str]) -> bool:
    """
    Filtert unzulässige Zustände für Topologie 2.

    Laut Aufgabenstellung:
    - nur ein Kabel gleichzeitig in Wartung
    """
    kabel_1_maintenance = state["kabel_1"] == "maintenance"
    kabel_2_maintenance = state["kabel_2"] == "maintenance"

    if kabel_1_maintenance and kabel_2_maintenance:
        return False

    return True


def analyze_topology_2(
    freileitung_links: Component,
    freileitung_rechts: Component,
    schaltfeld_links: Component,
    schaltfeld_rechts: Component,
    kabel_1: Component,
    kabel_2: Component,
    schaltfeld_kabel_1_links: Component,
    schaltfeld_kabel_1_rechts: Component,
    schaltfeld_kabel_2_links: Component,
    schaltfeld_kabel_2_rechts: Component,
) -> Topology2AnalysisResult:
    """
    Analysiert Topologie 2 über vollständige Zustandsenumeration.

    Komponenten:
    - Freileitung links / rechts
    - gemeinsames Schaltfeld links / rechts
    - Kabelzweig 1: Schaltfeld links - Kabel 1 - Schaltfeld rechts
    - Kabelzweig 2: Schaltfeld links - Kabel 2 - Schaltfeld rechts

    Ergebnis:
    - Wahrscheinlichkeit jeder Kapazitätsstufe
    - Nicht-Verfügbarkeit der Übertragungsstrecke
    """

    components = {
        "freileitung_links": freileitung_links,
        "freileitung_rechts": freileitung_rechts,
        "schaltfeld_links": schaltfeld_links,
        "schaltfeld_rechts": schaltfeld_rechts,
        "kabel_1": kabel_1,
        "kabel_2": kabel_2,
        "schaltfeld_kabel_1_links": schaltfeld_kabel_1_links,
        "schaltfeld_kabel_1_rechts": schaltfeld_kabel_1_rechts,
        "schaltfeld_kabel_2_links": schaltfeld_kabel_2_links,
        "schaltfeld_kabel_2_rechts": schaltfeld_kabel_2_rechts,
    }

    component_state_probabilities = {
        name: get_component_state_probabilities(component)
        for name, component in components.items()
    }

    component_state_lists = {
        name: list(state_probs.keys())
        for name, state_probs in component_state_probabilities.items()
    }

    state_evaluations: List[StateEvaluation] = []
    capacity_probabilities: Dict[float, float] = {}

    total_generated_states = 0
    valid_states = 0
    skipped_states = 0

    all_state_combinations = product(
        component_state_lists["freileitung_links"],
        component_state_lists["freileitung_rechts"],
        component_state_lists["schaltfeld_links"],
        component_state_lists["schaltfeld_rechts"],
        component_state_lists["kabel_1"],
        component_state_lists["kabel_2"],
        component_state_lists["schaltfeld_kabel_1_links"],
        component_state_lists["schaltfeld_kabel_1_rechts"],
        component_state_lists["schaltfeld_kabel_2_links"],
        component_state_lists["schaltfeld_kabel_2_rechts"],
    )

    for (
        freileitung_links_state,
        freileitung_rechts_state,
        schaltfeld_links_state,
        schaltfeld_rechts_state,
        kabel_1_state,
        kabel_2_state,
        schaltfeld_kabel_1_links_state,
        schaltfeld_kabel_1_rechts_state,
        schaltfeld_kabel_2_links_state,
        schaltfeld_kabel_2_rechts_state,
    ) in all_state_combinations:
        total_generated_states += 1

        state = {
            "freileitung_links": freileitung_links_state,
            "freileitung_rechts": freileitung_rechts_state,
            "schaltfeld_links": schaltfeld_links_state,
            "schaltfeld_rechts": schaltfeld_rechts_state,
            "kabel_1": kabel_1_state,
            "kabel_2": kabel_2_state,
            "schaltfeld_kabel_1_links": schaltfeld_kabel_1_links_state,
            "schaltfeld_kabel_1_rechts": schaltfeld_kabel_1_rechts_state,
            "schaltfeld_kabel_2_links": schaltfeld_kabel_2_links_state,
            "schaltfeld_kabel_2_rechts": schaltfeld_kabel_2_rechts_state,
        }

        if not is_valid_topology_2_state(state):
            skipped_states += 1
            continue

        valid_states += 1

        probability = compute_state_probability(state, component_state_probabilities)

        topology_result = evaluate_topology_2(
            freileitung_links_state=state["freileitung_links"],
            freileitung_rechts_state=state["freileitung_rechts"],
            schaltfeld_links_state=state["schaltfeld_links"],
            schaltfeld_rechts_state=state["schaltfeld_rechts"],
            kabel_1_state=state["kabel_1"],
            kabel_2_state=state["kabel_2"],
            schaltfeld_kabel_1_links_state=state["schaltfeld_kabel_1_links"],
            schaltfeld_kabel_1_rechts_state=state["schaltfeld_kabel_1_rechts"],
            schaltfeld_kabel_2_links_state=state["schaltfeld_kabel_2_links"],
            schaltfeld_kabel_2_rechts_state=state["schaltfeld_kabel_2_rechts"],
        )

        state_evaluations.append(
            StateEvaluation(
                state=state,
                probability=probability,
                topology_result=topology_result,
            )
        )

        capacity = topology_result.available_capacity_fraction
        capacity_probabilities[capacity] = (
            capacity_probabilities.get(capacity, 0.0) + probability
        )

    non_availability = capacity_probabilities.get(0.0, 0.0)

    total_probability = sum(capacity_probabilities.values())
    if total_probability <= 0.0:
        raise ValueError(
            "Keine gültigen Zustände mit positiver Wahrscheinlichkeit für Topologie 2 berechnet."
        )

    if total_probability > 1.000001:
        raise ValueError(
            f"Summe der Zustandswahrscheinlichkeiten > 1 bei Topologie 2: {total_probability:.8f}"
        )

    return Topology2AnalysisResult(
        state_evaluations=state_evaluations,
        capacity_probabilities=capacity_probabilities,
        non_availability=non_availability,
    )


# =========================================================
# Ausgabehilfen Topologie 2
# =========================================================


def print_topology_2_analysis(result: Topology2AnalysisResult) -> None:
    print("\n" + "=" * 90)
    print("Analyseergebnis Topologie 2")
    print("=" * 90)

    print("\nWahrscheinlichkeit je Kapazitätsstufe:")
    for capacity in sorted(result.capacity_probabilities.keys(), reverse=True):
        probability = result.capacity_probabilities[capacity]
        print(f"  Kapazität {capacity:>4.1f} : {probability:.8f}")

    p_full = result.capacity_probabilities.get(1.0, 0.0)
    p_half = result.capacity_probabilities.get(0.5, 0.0)
    p_zero = result.capacity_probabilities.get(0.0, 0.0)

    print("\n" + "-" * 90)
    print("Zusammenfassung:")
    print(f"  P(100% Kapazität) : {p_full:.8f}")
    print(f"  P( 50% Kapazität) : {p_half:.8f}")
    print(f"  P(  0% Kapazität) : {p_zero:.8f}")

    print("\n" + "-" * 90)
    print(f"Nicht-Verfügbarkeit der Übertragungsstrecke: {result.non_availability:.8f}")

    availability = 1.0 - result.non_availability
    print(f"Verfügbarkeit der Übertragungsstrecke:     {availability:.8f}")

    print("\n" + "-" * 90)
    total_probability = sum(result.capacity_probabilities.values())
    print(f"Summe der Zustandswahrscheinlichkeiten:     {total_probability:.8f}")

    if abs(total_probability - 1.0) > 1e-6:
        print("⚠️ WARNUNG: Wahrscheinlichkeiten summieren sich nicht zu 1!")
    else:
        print("✔ Wahrscheinlichkeiten konsistent (≈ 1.0)")

    print("=" * 90)


def print_topology_2_states(result: Topology2AnalysisResult, limit: int = 20) -> None:
    """
    Gibt die ersten Zustände zur Kontrolle aus.
    """
    print("\n" + "=" * 110)
    print(f"Erste {limit} Zustände Topologie 2")
    print("=" * 110)

    for i, evaluation in enumerate(result.state_evaluations[:limit], start=1):
        state = evaluation.state
        print(
            f"{i:>2d}. "
            f"FL links={state['freileitung_links']}, "
            f"SF links={state['schaltfeld_links']}, "
            f"K1-SF links={state['schaltfeld_kabel_1_links']}, "
            f"K1={state['kabel_1']}, "
            f"K1-SF rechts={state['schaltfeld_kabel_1_rechts']}, "
            f"K2-SF links={state['schaltfeld_kabel_2_links']}, "
            f"K2={state['kabel_2']}, "
            f"K2-SF rechts={state['schaltfeld_kabel_2_rechts']}, "
            f"SF rechts={state['schaltfeld_rechts']}, "
            f"FL rechts={state['freileitung_rechts']} | "
            f"P={evaluation.probability:.8f} | "
            f"Kapazität={evaluation.topology_result.available_capacity_fraction:.1f} | "
            f"{evaluation.topology_result.description}"
        )
