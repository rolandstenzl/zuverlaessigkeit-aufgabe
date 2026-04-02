from dataclasses import dataclass

@dataclass
class ReliabilityDataset:
    name: str
    H_trenner: float
    T_trenner_h: float
    H_leistungsschalter: float
    T_leistungsschalter_h: float
    H_sammelschiene: float
    T_sammelschiene_h: float
    H_freileitung_per_km: float
    T_freileitung_h: float
    H_kabel_per_km: float
    T_kabel_h: float
    maintenance_interval_years: float
    maintenance_duration_days_per_km: float
