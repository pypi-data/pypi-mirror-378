from copy import deepcopy

from aiospb.hosts import MinMetricInfo, MinMetricInfoCache
from aiospb.nodes import (
    Historian,
    MetricInfo,
    MetricNotFound,
    MetricsNetwork,
    Reading,
    ReadingStore,
)
from aiospb.shared import DataType, DeviceKey, Metric, Quality, ValueType


class InMemHistorian(Historian):
    """Implementation of historian in memory,

    for acceptance tests purpose"""

    def __init__(self):
        self._data = {}

    async def save(self, key: DeviceKey, metrics: list[Metric]):
        if key not in self._data:
            self._data[key] = []

        metrics = deepcopy(metrics)
        for metric in metrics:
            metric.is_historical = True
        self._data[key].extend(metrics)

    async def load(self, key: DeviceKey) -> list[Metric]:
        if key not in self._data:
            return []
        return self._data[key]

    async def clear(self, key: DeviceKey):
        self._data.pop(key)

    def get_device_keys(self, node_key: DeviceKey) -> list[DeviceKey]:
        return [key for key in self._data.keys() if key.node == node_key]


class InMemReadingStore(ReadingStore):
    """Implementation in RAM memory, not valid if too much metrics"""

    def __init__(self):
        self._readings = {}

    async def get(self, aliases: list[int]) -> list[Reading]:
        return [
            self._readings.get(alias, Reading(None, DataType.Unknown, Quality.BAD))
            for alias in aliases
        ]

    async def set(self, readings: dict[int, Reading]):
        self._readings.update(readings)


class InMemMinMetricInfoCache(MinMetricInfoCache):
    """Implementation in RAM memory,

    for low quantity of connected nodes and metrics, otherwise use fs"""

    def __init__(self):
        self._data = {}

    async def get(self, key: DeviceKey, names: list[str]) -> list[MinMetricInfo]:
        if key not in self._data:
            return [MinMetricInfo(DataType.Unknown)] * len(names)

        return [
            self._data[key].get(name, MinMetricInfo(DataType.Unknown)) for name in names
        ]

    async def set(self, key: DeviceKey, info: dict[str, MinMetricInfo]):
        if key not in self._data:
            self._data[key] = {}

        self._data[key].update(info)

    async def remove(self, key: DeviceKey):
        self._data.pop(key, None)
