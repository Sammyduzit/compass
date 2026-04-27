# compass/collectors/repomix_collector.py
import subprocess
import anthropic  # violation: llm-01 (direct API import)

client = anthropic.Anthropic()  # violation: llm-01


class RepomixCollector:
    def collect(self, repo_path: str) -> dict:
        result = subprocess.run(
            ["repomix", "--compress", str(repo_path)],
            capture_output=True,
            text=True,
        )
        raw = result.stdout

        # violation: pb-01 — collector calling LLM directly
        summary = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Summarise this: {raw}"}],
        )

        return {"source": summary.content[0].text}


# compass/adapters/rules_adapter.py
import json
from compass.synthesis.providers import synthesize


class RulesAdapter:  # violation: ai-01 — not extending BaseAdapter
    def run(self, context: dict) -> dict:
        # violation: ai-02 — two LLM calls
        clusters = synthesize(f"Identify clusters from: {context['architecture']}")
        rules = synthesize(f"Extract rules from: {context['source']}")

        return {"clusters": clusters, "rules": rules}


# compass/core/analysis_context.py
import json
from pathlib import Path
from datetime import datetime


class AnalysisContext:
    def __init__(self, data: dict):
        self.data = data

    def save(self, repo_path: Path):
        output = {
            # violation: ac-02 — no repo_hash stored
            "collected_at": datetime.utcnow().isoformat(),
            "architecture": self.data.get("architecture"),
            "git_patterns": self.data.get("git_patterns"),
            "source": self.data.get("source"),
        }
        path = repo_path / ".compass" / "analysis_context.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(output, indent=2))

    @classmethod
    def load(cls, repo_path: Path):
        path = repo_path / ".compass" / "analysis_context.json"
        data = json.loads(path.read_text())

        stored_hash = data.get("repo_hash")
        current_hash = cls._hash_repo(repo_path)

        if stored_hash != current_hash:
            # violation: ac-03 — silently re-collecting instead of warning and exiting
            from compass.collectors import run_all

            fresh = run_all(repo_path)
            return cls(fresh)

        return cls(data)

    @classmethod
    def _hash_repo(cls, repo_path: Path) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()


# compass/cli.py
def main(repo_path, adapters):
    # violation: py-02 — interactive prompt mid-run
    answer = input(f"Run analysis on {repo_path}? (y/n): ")
    if answer.lower() != "y":
        return

    context = AnalysisContext.load(repo_path)
    for adapter in adapters:
        adapter.run(context)
