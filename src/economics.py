import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

# =========================================================
# Konstanten aus der Aufgabenstellung
# =========================================================

COST_PER_SWITCHGEAR_EUR = 3_500_000.0
ADDITIONAL_SWITCHGEAR_FIELDS_TOPOLOGY_2 = 6
DEPRECIATION_YEARS = 25
INTEREST_RATE = 0.06

NOMINAL_GENERATION_POWER_MW = 300.0
COST_PER_UNSERVED_MWH_EUR = 350.0

# Erzeugungsprofil: (Anteil der Nennleistung, Stunden pro Jahr)
GENERATION_PROFILE: List[Tuple[float, float]] = [
    (0.00, 210.0),
    (0.25, 1520.0),
    (0.50, 4230.0),
    (0.75, 2300.0),
    (1.00, 500.0),
]

# Technische Übertragungskapazitäten
# Voll verfügbarer Transport: begrenzt auf die Erzeugungsnennleistung
FULL_CAPACITY_MW = 300.0

# Ein verfügbarer Kabelzweig in Topologie 2:
# P ≈ sqrt(3) * U * I = sqrt(3) * 220kV * 500A ≈ 190.5 MW
ONE_CABLE_BRANCH_CAPACITY_MW = math.sqrt(3.0) * 220_000.0 * 500.0 / 1_000_000.0

ZERO_CAPACITY_MW = 0.0


# =========================================================
# Datenklassen
# =========================================================


@dataclass
class CapacityCostBreakdown:
    capacity_fraction: float
    available_power_mw: float
    annual_unserved_energy_mwh: float
    annual_unserved_energy_cost_eur: float


@dataclass
class EconomicResult:
    annual_investment_cost_eur: float
    annual_unserved_energy_mwh: float
    annual_unserved_energy_cost_eur: float
    annual_total_cost_eur: float
    breakdown: List[CapacityCostBreakdown]


# =========================================================
# Grundfunktionen
# =========================================================


def annuity(investment_eur: float, interest_rate: float, years: int) -> float:
    """
    Berechnet die jährliche Annuität.

    Formel:
        A = I * [ i * (1+i)^n ] / [ (1+i)^n - 1 ]
    """
    if years <= 0:
        raise ValueError("years muss > 0 sein")

    if interest_rate == 0:
        return investment_eur / years

    q = 1.0 + interest_rate
    annuity_factor = (interest_rate * q**years) / (q**years - 1.0)
    return investment_eur * annuity_factor


def topology_2_additional_investment_eur() -> float:
    """
    Zusatzinvestition von Topologie 2 gegenüber Topologie 1.
    """
    return ADDITIONAL_SWITCHGEAR_FIELDS_TOPOLOGY_2 * COST_PER_SWITCHGEAR_EUR


def topology_2_annual_additional_investment_cost_eur() -> float:
    """
    Jährliche Zusatzkosten (Annuität) für die zusätzlichen Schaltfelder von Topologie 2.
    """
    investment = topology_2_additional_investment_eur()
    return annuity(
        investment_eur=investment,
        interest_rate=INTEREST_RATE,
        years=DEPRECIATION_YEARS,
    )


# =========================================================
# Kapazitätsabbildung
# =========================================================


def topology_1_capacity_fraction_to_mw(capacity_fraction: float) -> float:
    """
    Abbildung der Kapazitätszustände von Topologie 1 auf MW.

    Nach deinem bisherigen Modell:
    - 1.0 -> 300 MW
    - 0.0 -> 0 MW
    - 0.5 wird nicht erwartet, wird aber defensiv auf 150 MW gesetzt
    """
    if capacity_fraction == 1.0:
        return FULL_CAPACITY_MW
    if capacity_fraction == 0.5:
        return 0.5 * FULL_CAPACITY_MW
    if capacity_fraction == 0.0:
        return ZERO_CAPACITY_MW

    raise ValueError(f"Unbekannte Kapazitätsstufe für Topologie 1: {capacity_fraction}")


def topology_2_capacity_fraction_to_mw(capacity_fraction: float) -> float:
    """
    Abbildung der Kapazitätszustände von Topologie 2 auf MW.

    Wichtig:
    - 1.0 -> volle Übertragbarkeit bis 300 MW
    - 0.5 -> ein Kabelzweig verfügbar -> ca. 190.5 MW
    - 0.0 -> 0 MW
    """
    if capacity_fraction == 1.0:
        return FULL_CAPACITY_MW
    if capacity_fraction == 0.5:
        return ONE_CABLE_BRANCH_CAPACITY_MW
    if capacity_fraction == 0.0:
        return ZERO_CAPACITY_MW

    raise ValueError(f"Unbekannte Kapazitätsstufe für Topologie 2: {capacity_fraction}")


# =========================================================
# Kostenberechnung
# =========================================================


def compute_unserved_energy_for_capacity_state(
    available_power_mw: float,
    nominal_generation_power_mw: float = NOMINAL_GENERATION_POWER_MW,
    generation_profile: List[Tuple[float, float]] = GENERATION_PROFILE,
) -> float:
    """
    Berechnet die jährlich nicht gelieferte Energie [MWh]
    für eine gegebene verfügbare Netzkapazität in MW.

    Für jede Erzeugungsstufe:
        Erzeugungsleistung = Anteil * Nennleistung
        Defizit = max(0, Erzeugung - verfügbare Netzkapazität)
        Energie = Defizit * Stunden
    """
    annual_unserved_energy_mwh = 0.0

    for generation_fraction, hours in generation_profile:
        generation_power_mw = generation_fraction * nominal_generation_power_mw
        deficit_mw = max(0.0, generation_power_mw - available_power_mw)
        annual_unserved_energy_mwh += deficit_mw * hours

    return annual_unserved_energy_mwh


def compute_unserved_energy_costs(
    capacity_probabilities: Dict[float, float],
    capacity_fraction_to_mw_func,
    cost_per_unserved_mwh_eur: float = COST_PER_UNSERVED_MWH_EUR,
    nominal_generation_power_mw: float = NOMINAL_GENERATION_POWER_MW,
    generation_profile: List[Tuple[float, float]] = GENERATION_PROFILE,
) -> Tuple[float, float, List[CapacityCostBreakdown]]:
    """
    Berechnet die erwarteten jährlichen Kosten der nicht gelieferten Energie
    aus den Wahrscheinlichkeiten der Kapazitätszustände.

    Erwartungswert:
        Summe über alle Kapazitätszustände:
            P(Zustand) * ENS(Zustand)
    """
    total_expected_unserved_energy_mwh = 0.0
    total_expected_cost_eur = 0.0
    breakdown: List[CapacityCostBreakdown] = []

    for capacity_fraction, probability in sorted(
        capacity_probabilities.items(), reverse=True
    ):
        available_power_mw = capacity_fraction_to_mw_func(capacity_fraction)

        annual_unserved_energy_mwh_if_in_this_state = (
            compute_unserved_energy_for_capacity_state(
                available_power_mw=available_power_mw,
                nominal_generation_power_mw=nominal_generation_power_mw,
                generation_profile=generation_profile,
            )
        )

        expected_unserved_energy_mwh = (
            probability * annual_unserved_energy_mwh_if_in_this_state
        )
        expected_cost_eur = expected_unserved_energy_mwh * cost_per_unserved_mwh_eur

        total_expected_unserved_energy_mwh += expected_unserved_energy_mwh
        total_expected_cost_eur += expected_cost_eur

        breakdown.append(
            CapacityCostBreakdown(
                capacity_fraction=capacity_fraction,
                available_power_mw=available_power_mw,
                annual_unserved_energy_mwh=expected_unserved_energy_mwh,
                annual_unserved_energy_cost_eur=expected_cost_eur,
            )
        )

    return total_expected_unserved_energy_mwh, total_expected_cost_eur, breakdown


def evaluate_topology_1_economics(
    capacity_probabilities: Dict[float, float],
) -> EconomicResult:
    """
    Wirtschaftliche Bewertung von Topologie 1.

    Annahme:
    - keine zusätzlichen Investitionskosten gegenüber der Referenz
    """
    annual_unserved_energy_mwh, annual_unserved_energy_cost_eur, breakdown = (
        compute_unserved_energy_costs(
            capacity_probabilities=capacity_probabilities,
            capacity_fraction_to_mw_func=topology_1_capacity_fraction_to_mw,
        )
    )

    annual_investment_cost_eur = 0.0
    annual_total_cost_eur = annual_investment_cost_eur + annual_unserved_energy_cost_eur

    return EconomicResult(
        annual_investment_cost_eur=annual_investment_cost_eur,
        annual_unserved_energy_mwh=annual_unserved_energy_mwh,
        annual_unserved_energy_cost_eur=annual_unserved_energy_cost_eur,
        annual_total_cost_eur=annual_total_cost_eur,
        breakdown=breakdown,
    )


def evaluate_topology_2_economics(
    capacity_probabilities: Dict[float, float],
) -> EconomicResult:
    """
    Wirtschaftliche Bewertung von Topologie 2.

    Annahme:
    - 6 zusätzliche Schaltfelder à 3.5 Mio EUR
    - jährliche Zusatzkosten über Annuität
    """
    annual_unserved_energy_mwh, annual_unserved_energy_cost_eur, breakdown = (
        compute_unserved_energy_costs(
            capacity_probabilities=capacity_probabilities,
            capacity_fraction_to_mw_func=topology_2_capacity_fraction_to_mw,
        )
    )

    annual_investment_cost_eur = topology_2_annual_additional_investment_cost_eur()
    annual_total_cost_eur = annual_investment_cost_eur + annual_unserved_energy_cost_eur

    return EconomicResult(
        annual_investment_cost_eur=annual_investment_cost_eur,
        annual_unserved_energy_mwh=annual_unserved_energy_mwh,
        annual_unserved_energy_cost_eur=annual_unserved_energy_cost_eur,
        annual_total_cost_eur=annual_total_cost_eur,
        breakdown=breakdown,
    )


# =========================================================
# Ausgabehilfen
# =========================================================


def print_economic_result(title: str, result: EconomicResult) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

    print(
        f"Jährliche Investitionskosten [EUR/a]:       {result.annual_investment_cost_eur:,.2f}"
    )
    print(
        f"Jährlich nicht gelieferte Energie [MWh/a]:  {result.annual_unserved_energy_mwh:,.6f}"
    )
    print(
        f"Jährliche ENS-Kosten [EUR/a]:               {result.annual_unserved_energy_cost_eur:,.2f}"
    )
    print(
        f"Jährliche Gesamtkosten [EUR/a]:             {result.annual_total_cost_eur:,.2f}"
    )

    print("\nBeitrag der Kapazitätszustände:")
    for item in result.breakdown:
        print(
            f"  Kapazität={item.capacity_fraction:>4.1f} | "
            f"MW verfügbar={item.available_power_mw:>8.3f} | "
            f"ENS={item.annual_unserved_energy_mwh:>12.6f} MWh/a | "
            f"Kosten={item.annual_unserved_energy_cost_eur:>14.2f} EUR/a"
        )


def print_economic_comparison(
    topology_1_result: EconomicResult,
    topology_2_result: EconomicResult,
) -> None:
    print("\n" + "#" * 90)
    print("Wirtschaftlicher Vergleich Topologie 1 vs. Topologie 2")
    print("#" * 90)

    print(
        f"Topologie 1 Gesamtkosten [EUR/a]: {topology_1_result.annual_total_cost_eur:,.2f}"
    )
    print(
        f"Topologie 2 Gesamtkosten [EUR/a]: {topology_2_result.annual_total_cost_eur:,.2f}"
    )

    delta = (
        topology_2_result.annual_total_cost_eur
        - topology_1_result.annual_total_cost_eur
    )
    print(f"Differenz T2 - T1 [EUR/a]:        {delta:,.2f}")

    if (
        topology_1_result.annual_total_cost_eur
        < topology_2_result.annual_total_cost_eur
    ):
        print("=> Wirtschaftlich günstiger: Topologie 1")
    elif (
        topology_2_result.annual_total_cost_eur
        < topology_1_result.annual_total_cost_eur
    ):
        print("=> Wirtschaftlich günstiger: Topologie 2")
    else:
        print("=> Beide Topologien sind wirtschaftlich gleich")
