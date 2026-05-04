from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar('T')


class BaseCollector(ABC, Generic[T]):
	@abstractmethod
	async def collect(self, target_path: Path) -> T: ...
