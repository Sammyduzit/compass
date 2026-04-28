from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from compass.adapters.orchestrator import Orchestrator
from compass.config import CompassConfig
from compass.errors import AdapterError


def _config(adapters: list[str], provider: str = 'claude') -> CompassConfig:
	return CompassConfig(target_path='/tmp/repo', adapters=adapters, provider=provider)


def _mock_adapter_cls(name: str, *, fail: bool = False) -> type:
	instance = MagicMock()
	if fail:
		instance.run = AsyncMock(side_effect=AdapterError(name, 'something went wrong'))
	else:
		instance.run = AsyncMock()
	cls = MagicMock(return_value=instance)
	return cls


async def test_orchestrator_runs_registered_adapter():
	mock_cls = _mock_adapter_cls('rules')
	registry = {'rules': mock_cls}
	config = _config(['rules'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	mock_cls.return_value.run.assert_called_once()


async def test_orchestrator_skips_unknown_adapter():
	config = _config(['unknown_adapter'])
	registry: dict = {}

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()


async def test_orchestrator_continues_after_adapter_failure():
	failing_cls = _mock_adapter_cls('rules', fail=True)
	passing_cls = _mock_adapter_cls('summary')
	registry = {'rules': failing_cls, 'summary': passing_cls}
	config = _config(['rules', 'summary'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	passing_cls.return_value.run.assert_called_once()


async def test_orchestrator_runs_only_requested_adapters():
	rules_cls = _mock_adapter_cls('rules')
	summary_cls = _mock_adapter_cls('summary')
	registry = {'rules': rules_cls, 'summary': summary_cls}
	config = _config(['rules'])

	with patch('compass.adapters.orchestrator.ADAPTER_REGISTRY', registry):
		orchestrator = Orchestrator(config)
		await orchestrator.run()

	rules_cls.return_value.run.assert_called_once()
	summary_cls.return_value.run.assert_not_called()
