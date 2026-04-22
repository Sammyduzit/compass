import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from compass.collectors.base import BaseCollector
from compass.domain.coupling_pair import CouplingPair
from compass.domain.git_patterns_snapshot import GitPatternsSnapshot
from compass.errors import CollectorError


@dataclass
class FileGitData:
    churn: float
    age: int
    coupling_pairs: list[str]


@dataclass
class GitLogResult:
    file_data: dict[str, FileGitData]
    coupling_pairs: list[CouplingPair]
    git_patterns: GitPatternsSnapshot


class GitLogCollector(BaseCollector[GitLogResult]):
    async def collect(self, target_path: Path) -> GitLogResult:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--name-only",
            "--format=COMMIT %H",
            cwd=target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode()

        if proc.returncode != 0:
            raise CollectorError("GitLogCollector", f"{target_path} is not a git repository")

        commits = {}
        commit_hash = None
        for line in output.strip().split("\n"):
            if line.startswith("COMMIT"):
                commit_hash = line.strip().split(" ")[1]
                commits[commit_hash] = []
            elif line.strip() == "":
                continue
            elif commit_hash is not None:
                commits[commit_hash].append(line)

        file_counter = {}
        for list_of_files in commits.values():
            for file in list_of_files:
                file_counter[file] = file_counter.get(file, 0) + 1

        max_count = max(file_counter.values()) if file_counter else 1

        churn = {}
        for file_name, file_count in file_counter.items():
            churn_rate = file_count / max_count
            churn[file_name] = churn_rate

        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--name-only",
            "--format=COMMIT %ct",
            cwd=target_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode()

        if proc.returncode != 0:
            raise CollectorError("GitLogCollector", f"{target_path} is not a git repository")

        age = {}
        now = datetime.now(timezone.utc).timestamp()
        timestamp = 0
        for line in output.strip().split("\n"):
            if line.startswith("COMMIT"):
                timestamp = line.strip().split(" ")[1]
            elif line.strip() == "":
                continue
            elif line not in age:
                age[line] = int((now - float(timestamp)) / 86400)

        coupling_pairs = {}
        for files in commits.values():
            for file_a, file_b in combinations(files, 2):
                key = tuple(sorted([file_a, file_b]))
                coupling_pairs[key] = coupling_pairs.get(key, 0) + 1

        coupling_pairs_list = [
            CouplingPair(file_a=file_a, file_b=file_b, degree=degree)
            for (file_a, file_b), degree in coupling_pairs.items()
        ]

        file_coupling: dict[str, list[str]] = {}
        for file_a, file_b in coupling_pairs.keys():
            file_coupling.setdefault(file_a, []).append(file_b)
            file_coupling.setdefault(file_b, []).append(file_a)

        file_data: dict[str, FileGitData] = {}
        for file in file_counter.keys():
            file_churn = churn[file]
            file_age = age.get(file, 0)
            file_pairs = file_coupling.get(file, [])
            file_data[file] = FileGitData(
                churn=file_churn, age=file_age, coupling_pairs=file_pairs
            )

        sorted_by_churn = sorted(churn.items(), key=lambda x: x[1], reverse=True)
        hotspots = [f for f, _ in sorted_by_churn[:10]]
        stable_files = [f for f, _ in sorted_by_churn[-10:]]

        coupling_clusters = [
            list(cluster)
            for cluster in {
                frozenset([p.file_a, p.file_b]) for p in coupling_pairs_list
            }
        ]

        git_patterns = GitPatternsSnapshot(
            hotspots=hotspots,
            stable_files=stable_files,
            coupling_clusters=coupling_clusters,
        )

        return GitLogResult(
            file_data=file_data,
            coupling_pairs=coupling_pairs_list,
            git_patterns=git_patterns,
        )
