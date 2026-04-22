import dataclasses
import json
from pathlib import Path

import dacite
from dacite import Config
import pytest

from compass.domain.adapter_output import AdapterOutput
from compass.domain.analysis_context import AnalysisContext
from compass.domain.architecture_snapshot import ArchitectureSnapshot
from compass.domain.cluster import Cluster
from compass.domain.coupling_pair import CouplingPair
from compass.domain.file_score import FileScore
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot


def test_coupling_pair_fields():
	pair = CouplingPair(file_a='a.py', file_b='b.py', degree=5)
	assert pair.file_a == 'a.py'
	assert pair.file_b == 'b.py'
	assert pair.degree == 5


def test_file_score_fields():
	file_score = FileScore(
		path='tests/test_routes.py',
		churn=0.76,
		age=3,
		centrality=0.19,
		cluster_id=3,
		coupling_pairs=['src/api/routes.py'],
	)
	assert file_score.path == 'tests/test_routes.py'
	assert file_score.churn == 0.76
	assert file_score.age == 3
	assert file_score.centrality == 0.19
	assert file_score.cluster_id == 3
	assert file_score.coupling_pairs == ['src/api/routes.py']


def test_models_are_frozen():
	pair = CouplingPair(file_a='a.py', file_b='b.py', degree=5)
	with pytest.raises(dataclasses.FrozenInstanceError):
		pair.file_a = 'other.py'

	score = FileScore(
		path='a.py', churn=0.1, age=1, centrality=0.5, cluster_id=0, coupling_pairs=[]
	)
	with pytest.raises(dataclasses.FrozenInstanceError):
		score.path = 'other.py'

	cluster = Cluster(id=0, files=['a.py'])
	with pytest.raises(dataclasses.FrozenInstanceError):
		cluster.id = 1

	snapshot = ArchitectureSnapshot(file_scores=[], coupling_pairs=[], clusters=[])
	with pytest.raises(dataclasses.FrozenInstanceError):
		snapshot.file_scores = []

	git = GitPatternsSnapshot(hotspots=[], stable_files=[], coupling_clusters=[])
	with pytest.raises(dataclasses.FrozenInstanceError):
		git.hotspots = []

	output = AdapterOutput(adapter_name='rules', content='yaml')
	with pytest.raises(dataclasses.FrozenInstanceError):
		output.content = 'other'


def test_architecture_snapshot_fields():
	cluster = Cluster(id=0, files=['a.py', 'b.py'])
	score = FileScore(
		path='a.py', churn=0.1, age=1, centrality=0.5, cluster_id=0, coupling_pairs=[]
	)
	pair = CouplingPair(file_a='a.py', file_b='b.py', degree=10)
	snapshot = ArchitectureSnapshot(file_scores=[score], coupling_pairs=[pair], clusters=[cluster])
	assert snapshot.file_scores == [score]
	assert snapshot.coupling_pairs == [pair]
	assert snapshot.clusters == [cluster]


def test_git_patterns_snapshot_fields():
	git = GitPatternsSnapshot(
		hotspots=['a.py'],
		stable_files=['b.py'],
		coupling_clusters=[['a.py', 'b.py']],
	)
	assert git.hotspots == ['a.py']
	assert git.stable_files == ['b.py']
	assert git.coupling_clusters == [['a.py', 'b.py']]


def test_adapter_output_fields():
	output = AdapterOutput(adapter_name='rules', content='some yaml')
	assert output.adapter_name == 'rules'
	assert output.content == 'some yaml'


def test_analysis_context_deserialization():
	json_path = Path(__file__).parent.parent.parent / 'examples' / 'analysis_context.json'
	data = json.loads(json_path.read_text())
	context = dacite.from_dict(AnalysisContext, data, config=Config(cast=[tuple]))
	assert isinstance(context, AnalysisContext)
	assert isinstance(context.architecture, ArchitectureSnapshot)
	assert isinstance(context.architecture.file_scores[0], FileScore)
	assert isinstance(context.architecture.coupling_pairs[0], CouplingPair)
	assert isinstance(context.git_patterns, GitPatternsSnapshot)


def test_analysis_context_serialization_roundtrip():
	json_path = Path(__file__).parent.parent.parent / 'examples' / 'analysis_context.json'
	data = json.loads(json_path.read_text())
	context = dacite.from_dict(AnalysisContext, data, config=Config(cast=[tuple]))
	serialized = dataclasses.asdict(context)
	assert (
		serialized['architecture']['file_scores'][0]['path']
		== data['architecture']['file_scores'][0]['path']
	)
	assert serialized['docs'] == data['docs']
