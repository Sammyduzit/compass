from domain.coupling_pair import CouplingPair
from domain.file_score import FileScore


def test_coupling_pair_fields():
    pair = CouplingPair(file_a="a.py", file_b="b.py", degree=5)
    assert pair.file_a == "a.py"
    assert pair.file_b == "b.py"
    assert pair.degree == 5

def test_file_score_fields():
    file_scores = FileScore( path="tests/test_routes.py", churn=0.76, age=3, centrality=0.19, cluster_id=3, coupling_pairs=["src/api/routes.py"])
    assert file_scores.path == "tests/test_routes.py"
    assert file_scores.churn == 0.76
    assert file_scores.age == 3
    assert file_scores.centrality == 0.19
    assert file_scores.cluster_id == 3
    assert file_scores.coupling_pairs == ["src/api/routes.py"]
