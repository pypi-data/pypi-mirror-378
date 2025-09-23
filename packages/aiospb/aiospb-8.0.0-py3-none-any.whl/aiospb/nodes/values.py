from dataclasses import dataclass, field

from typing import Self
from aiospb.shared import DataType, PropertySet, ValueType, Quality, Metric


@dataclass
class Reading:
    value: ValueType
    data_type: DataType = DataType.Unknown
    quality: Quality = Quality.GOOD

    def update(self, newer: Self) -> "Reading":
        value = newer.value if newer.quality == Quality.GOOD else self.value
        return Reading(value, self.data_type, newer.quality)

    def create_change_metric(
        self, timestamp: int, alias: int, newer: Self
    ) -> Metric | None:
        reading = self.update(newer)
        if reading == self:
            return

        metric = Metric(timestamp, reading.value, reading.data_type, alias, "")
        if reading.quality != self.quality:
            metric.quality = reading.quality

        return metric


@dataclass
class MetricInfo:
    """Stable metric data, stable during a session"""

    name: str
    data_type: DataType
    properties: PropertySet = field(default_factory=PropertySet)
    alias: int = 0
    is_transient: bool = False

    def create_birth_metric(self, timestamp: int, reading: Reading) -> Metric:
        """Create metric from the metric core"""
        metric = Metric(
            timestamp,
            reading.value,
            self.data_type,
            self.alias,
            self.name,
            self.properties,
            is_transient=self.is_transient,
        )

        if reading.quality != Quality.GOOD:
            metric.quality = reading.quality

        return metric
