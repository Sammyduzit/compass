from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from tests.conftest import setup_fixture_repo


@pytest.fixture
def integration_repo(tmp_path: Path) -> Callable[[str], Path]:
	"""Factory that recreates fixture repos and returns isolated git clones."""

	def _clone_fixture(name: str) -> Path:
		source_repo = setup_fixture_repo(name)
		clone_path = tmp_path / name
		subprocess.run(
			['git', 'clone', '--quiet', str(source_repo), str(clone_path)],
			check=True,
		)
		return clone_path

	return _clone_fixture


@pytest.fixture
def sample_analysis_context() -> AnalysisContext:
	return AnalysisContext(
		architecture=ArchitectureSnapshot(
			file_scores=[
				FileScore(
					path='README.md',
					churn=0.4,
					age=10,
					centrality=0.2,
					cluster_id=1,
					coupling_pairs=('notes.txt',),
				)
			],
			coupling_pairs=[CouplingPair(file_a='README.md', file_b='notes.txt', degree=2)],
			clusters=[Cluster(id=1, files=('README.md', 'notes.txt'))],
		),
		patterns={'naming': ['plain-text fixture']},
		git_patterns=GitPatternsSnapshot(
			hotspots=['README.md'],
			stable_files=['config.ini'],
			coupling_clusters=[['README.md', 'notes.txt']],
		),
		docs={'README.md': 'Minimal fixture repository used in integration tests.'},
	)


def commit_fixture_change(repo_path: Path, relative_path: str, content: str, message: str) -> None:
	"""Create a real git commit inside a synthetic fixture repository."""

	file_path = repo_path / relative_path
	file_path.write_text(content, encoding='utf-8')
	subprocess.run(['git', '-C', str(repo_path), 'add', relative_path], check=True)
	subprocess.run(['git', '-C', str(repo_path), 'commit', '--quiet', '-m', message], check=True)
