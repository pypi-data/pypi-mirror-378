import asyncio
import logging
from collections.abc import Callable
from typing import Coroutine

from aiospb.nodes.ports import DeviceConnectionIsBroken
from aiospb.nodes.values import Reading
from aiospb.shared import Clock, DeviceKey, Metric, Quality

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .devices import MetricsNetwork, ReadingStore


class Scanner:
    def __init__(
        self,
        key: DeviceKey,
        aliases: list[int],
        metrics_net: "MetricsNetwork",
        readings: "ReadingStore",
        callback: Callable[[list[Metric]], Coroutine[None, None, None]],
        clock: Clock,
    ):
        self._key = key
        self._net = metrics_net
        self._readings = readings
        self._callback = callback
        self._clock = clock
        self._aliases = aliases

        self._active_scans = set()
        self._loop_task = None

    async def _scan_loop(
        self,
        scan_rate: int,
    ):
        try:
            async for tick in self._clock.get_ticker(scan_rate):
                if self._active_scans:
                    logger.warning(
                        f"Starting a new scan at {tick}, but not finished {len(self._active_scans)} previous"
                    )

                scan = asyncio.create_task(self._scan(scan_rate), name=f"@{tick}")
                self._active_scans.add(scan)
                scan.add_done_callback(lambda task: self._active_scans.remove(task))

        except asyncio.CancelledError:
            for scan in self._active_scans:
                scan.cancel()
            return

    async def _scan(
        self,
        scan_rate: int,
    ):
        try:  # TODO: Manage self._readings exceptions
            last_values = await self._readings.get(self._aliases)
            tasks = [
                asyncio.create_task(self._read(alias, int(scan_rate * 0.9)))
                for alias in self._aliases
            ]
            await asyncio.wait(tasks)

            metrics = []
            readings = {}
            for last, task, alias in zip(last_values, tasks, self._aliases):
                ts, reading = task.result()
                metric = last.create_change_metric(ts, alias, reading)
                if metric:
                    metrics.append(metric)
                    readings[alias] = last.update(reading)

            if metrics:
                metrics = sorted(metrics, key=lambda m: m.timestamp)
                await self._callback(metrics)
                await self._readings.set(readings)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Scanning at {self._clock.timestamp()}")
            logger.exception(e)
            raise e

    async def _read(self, alias: int, timeout_ms: int) -> tuple[int, Reading]:
        try:
            value = await self._clock.wait_for(
                asyncio.create_task(self._net.read(self._key, alias)), timeout_ms
            )
        except TimeoutError:
            return (self._clock.timestamp(), Reading(None, quality=Quality.STALE))
        except DeviceConnectionIsBroken:
            return (self._clock.timestamp(), Reading(None, quality=Quality.STALE))
        except Exception as e:
            logger.error(f"Reading metric with alias {alias}")
            logger.exception(e)
            return (self._clock.timestamp(), Reading(None, quality=Quality.BAD))

        return (self._clock.timestamp(), Reading(value))

    def start(
        self,
        scan_rate: int,
    ):
        if self._loop_task:
            self._loop_task.cancel()

        self._loop_task = asyncio.create_task(self._scan_loop(scan_rate))

    def stop(self):
        if self._loop_task is None:
            return
        self._loop_task.cancel()

    def is_running(self):
        return not (self._loop_task is None or self._loop_task.done())
