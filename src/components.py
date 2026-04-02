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


@dataclass
class Component:
    name: str
    component_type: str
    failure_rate_per_year: float
    repair_time_hours: float
    maintenance_interval_years: float = 0.0
    maintenance_duration_days_per_km: float = 0.0
    length_km: float = 0.0

    @property
    def maintenance_frequency_per_year(self) -> float:
        """
        Wartungshäufigkeit H_w [1/a]
        Beispiel: Intervall 5 a -> H_w = 1/5 = 0.2 1/a
        """
        if self.maintenance_interval_years <= 0:
            return 0.0
        return 1.0 / self.maintenance_interval_years

    @property
    def maintenance_duration_hours(self) -> float:
        """
        Wartungsdauer pro Ereignis in Stunden.
        Nur relevant für längenabhängige Komponenten wie Kabel.
        """
        if self.length_km <= 0 or self.maintenance_duration_days_per_km <= 0:
            return 0.0
        return self.length_km * self.maintenance_duration_days_per_km * 24.0

    @property
    def nv_failure(self) -> float:
        """
        Nichtverfügbarkeit durch ungeplante Ausfälle, dimensionslos.
        NV = H * T / 8760
        """
        return (self.failure_rate_per_year * self.repair_time_hours) / 8760.0

    @property
    def nv_maintenance(self) -> float:
        """
        Nichtverfügbarkeit durch Wartung, dimensionslos.
        NV_w = H_w * T_w / 8760
        """
        return (
            self.maintenance_frequency_per_year * self.maintenance_duration_hours
        ) / 8760.0

    @property
    def nv_total(self) -> float:
        """
        Gesamtnichtverfügbarkeit als Summe aus Fehler- und Wartungsanteil.
        Für dieses einfache Anfangsmodell additiv.
        """
        return self.nv_failure + self.nv_maintenance

    @property
    def availability(self) -> float:
        """
        Verfügbarkeit V = 1 - NV
        """
        return 1.0 - self.nv_total

    def summary_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.component_type,
            "failure_rate_per_year": self.failure_rate_per_year,
            "repair_time_hours": self.repair_time_hours,
            "maintenance_frequency_per_year": self.maintenance_frequency_per_year,
            "maintenance_duration_hours": self.maintenance_duration_hours,
            "nv_failure": self.nv_failure,
            "nv_maintenance": self.nv_maintenance,
            "nv_total": self.nv_total,
            "availability": self.availability,
        }


def create_freileitung(name: str, dataset: ReliabilityDataset, length_km: float) -> Component:
    return Component(
        name=name,
        component_type="Freileitung",
        failure_rate_per_year=dataset.H_freileitung_per_km * length_km,
        repair_time_hours=dataset.T_freileitung_h,
        length_km=length_km,
    )


def create_kabel(name: str, dataset: ReliabilityDataset, length_km: float) -> Component:
    return Component(
        name=name,
        component_type="Erdkabel",
        failure_rate_per_year=dataset.H_kabel_per_km * length_km,
        repair_time_hours=dataset.T_kabel_h,
        maintenance_interval_years=dataset.maintenance_interval_years,
        maintenance_duration_days_per_km=dataset.maintenance_duration_days_per_km,
        length_km=length_km,
    )


def create_trenner(name: str, dataset: ReliabilityDataset) -> Component:
    return Component(
        name=name,
        component_type="Trenner",
        failure_rate_per_year=dataset.H_trenner,
        repair_time_hours=dataset.T_trenner_h,
    )


def create_leistungsschalter(name: str, dataset: ReliabilityDataset) -> Component:
    return Component(
        name=name,
        component_type="Leistungsschalter",
        failure_rate_per_year=dataset.H_leistungsschalter,
        repair_time_hours=dataset.T_leistungsschalter_h,
    )


def create_sammelschiene(name: str, dataset: ReliabilityDataset) -> Component:
    return Component(
        name=name,
        component_type="Sammelschiene",
        failure_rate_per_year=dataset.H_sammelschiene,
        repair_time_hours=dataset.T_sammelschiene_h,
    )
