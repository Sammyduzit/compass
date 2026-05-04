from __future__ import annotations

from compass.adapters.base import AdapterBase
from compass.config import CompassConfig
from compass.errors import AdapterError
from compass.log import get_logger
from compass.paths import compass_paths

log = get_logger(__name__)

# Populated as concrete adapters are implemented (issues #30, #31).
ADAPTER_REGISTRY: dict[str, type[AdapterBase]] = {}


class Orchestrator:
	def __init__(self, config: CompassConfig) -> None:
		self._config = config
		self._paths = compass_paths(config.target_path)

	async def run(self) -> None:
		for adapter_name in self._config.adapters:
			cls = ADAPTER_REGISTRY.get(adapter_name)
			if cls is None:
				log.warning('[%s] unknown adapter — skipping', adapter_name)
				continue
			adapter = cls(self._config, self._paths)
			try:
				await adapter.run()
			except AdapterError as exc:
				log.error('[%s] failed — %s', adapter_name, exc)
