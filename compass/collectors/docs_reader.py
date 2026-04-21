from pathlib import Path

from compass.collectors.base import BaseCollector
from compass.errors import CollectorError


class DocsReaderCollector(BaseCollector[dict[str, str]]):
    async def collect(self, target_path: Path) -> dict[str, str]:
        results: dict[str, str] = {}

        candidates = [
            target_path / "CONTRIBUTING.md",
            target_path / "README.md",
            target_path / ".cursor" / "rules",
        ]
        adr_dir = target_path / "docs" / "adr"
        if adr_dir.exists():
            candidates.extend(adr_dir.iterdir())

        for path in candidates:
            if path.exists():
                try:
                    results[str(path.relative_to(target_path))] = path.read_text()
                except OSError as e:
                    raise CollectorError(f"Failed to read {path}: {e}")
        return results
