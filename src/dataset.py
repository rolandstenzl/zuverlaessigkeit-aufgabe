from components import ReliabilityDataset

# =========================
# Datensatz 1 (Basis)
# =========================
dataset_1 = ReliabilityDataset(
    name="Datensatz 1",

    H_trenner=0.002494,
    T_trenner_h=7.447,

    H_leistungsschalter=0.002494,
    T_leistungsschalter_h=7.447,

    H_sammelschiene=0.000399,
    T_sammelschiene_h=4.704,

    H_freileitung_per_km=0.001945,
    T_freileitung_h=3.13,

    H_kabel_per_km=0.002262,
    T_kabel_h=48.76,

    maintenance_interval_years=5,
    maintenance_duration_days_per_km=0.5
)


# =========================
# Datensatz 2 (z. B. bessere Kabel)
# =========================
dataset_2 = ReliabilityDataset(
    name="Datensatz 2",

    H_trenner=0.002494,
    T_trenner_h=7.447,

    H_leistungsschalter=0.002494,
    T_leistungsschalter_h=7.447,

    H_sammelschiene=0.000399,
    T_sammelschiene_h=4.704,

    H_freileitung_per_km=0.001945,
    T_freileitung_h=3.13,

    H_kabel_per_km=0.001131,   # bessere Kabel (geringere Ausfallrate)
    T_kabel_h=48.76,

    maintenance_interval_years=5,
    maintenance_duration_days_per_km=0.2   # kürzere Wartung
)


# =========================
# Datensatz 3 (z. B. anderes Wartungsintervall)
# =========================
dataset_3 = ReliabilityDataset(
    name="Datensatz 3",

    H_trenner=0.002494,
    T_trenner_h=7.447,

    H_leistungsschalter=0.002494,
    T_leistungsschalter_h=7.447,

    H_sammelschiene=0.000399,
    T_sammelschiene_h=4.704,

    H_freileitung_per_km=0.001945,
    T_freileitung_h=3.13,

    H_kabel_per_km=0.002262,
    T_kabel_h=48.76,

    maintenance_interval_years=2,          # häufigere Wartung!
    maintenance_duration_days_per_km=0.5
)


# =========================
# Sammlung aller Datensätze
# =========================
ALL_DATASETS = [
    dataset_1,
    dataset_2,
    dataset_3
]
