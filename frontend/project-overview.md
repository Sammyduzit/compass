# Compass — Architecture Overview for Interns

> Five diagrams that cover the full system. Start with 1 and 2, dive into 3–5 when you go deeper.
>
> **VS Code:** Install [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) by Matt Bierner, then open preview with `Cmd+Shift+V`.
> **GitHub:** Diagrams render automatically — no setup needed.

---

## 1. Top-Level Architecture (Port-Adapter)

```mermaid
flowchart LR
    subgraph P1["Phase 1 — Collectors (no LLM)"]
        direction TB
        C1[ImportGraphCollector]
        C2[AstGrepCollector]
        C3[GitLogCollector]
        C4[DocsReaderCollector]
    end

    AC[(AnalysisContext<br>.compass/analysis_context.json)]

    subgraph P2["Phase 2 — Adapters (1 LLM call each)"]
        direction TB
        A1[RulesAdapter] --> O1[rules.yaml]
        A2[SummaryAdapter] --> O2[summary.md]
    end

    CLI[cli.py] --> Runner[runner.py]
    Runner --> P1
    P1 --> AC
    AC --> P2
```

---

## 2. Full Pipeline Flow (End-to-End)

```mermaid
flowchart TD
    Start([compass /path/to/repo --adapters rules,summary])
    Start --> CLI[cli.py<br>parse args → CompassConfig]
    CLI --> R[runner.py]
    R --> Pre[prerequisites.check<br>7 checks]
    Pre --> Lang[language_detection.detect<br>python · typescript · generic]
    Lang --> Stale{AnalysisContext<br>stale?}

    Stale -->|yes / --reanalyze| P1[Phase 1: CollectorOrchestrator]
    Stale -->|no| P2

    P1 --> Coll1[ImportGraphCollector<br>centrality + Louvain clusters]
    P1 --> Coll2[AstGrepCollector<br>error handling · naming]
    P1 --> Coll3[GitLogCollector<br>churn · coupling pairs · age]
    P1 --> Coll4[DocsReaderCollector<br>CONTRIBUTING.md · ADRs]

    Coll1 & Coll2 & Coll3 & Coll4 --> AC[(AnalysisContext<br>persisted JSON)]
    AC --> P2[Phase 2: AdapterOrchestrator]

    P2 --> RA[RulesAdapter] --> RO[rules.yaml]
    P2 --> SA[SummaryAdapter] --> SO[summary.md]
```

---

## 3. Adapter Runtime (Phase 2 Detail)

```mermaid
flowchart TD
    AC[(AnalysisContext)] --> FS["FileSelector<br>apply_coverage()"]
    FS --> GA[grep_ast<br>file skeletons]
    FS --> RM["repomix --compress<br>bodies — RulesAdapter only"]
    GA & RM --> BP[build_prompt<br>adapter-specific]
    BP --> LLM[Provider subprocess<br>claude · codex]
    LLM --> VAL{validate_output<br>schema check}
    VAL -->|OK| OUT[output_writer<br>rules.yaml / summary.md]
    VAL -->|fail| RET[1 retry]
    RET --> LLM
    RET -->|fail again| ERR([hard error])
```

---

## 4. Package Structure

```mermaid
flowchart TD
    ROOT[compass/]

    ROOT --> CLI[cli.py<br>entry point]
    ROOT --> RUN[runner.py<br>pipeline]
    ROOT --> MISC[config · language_detection<br>prerequisites · paths · log · errors]

    ROOT --> DOM[domain/]
    DOM --> D1[analysis_context.py]
    DOM --> D2[file_score.py]
    DOM --> D3[adapter_output.py · coupling_pair.py]

    ROOT --> COL[collectors/]
    COL --> CO1[import_graph.py]
    COL --> CO2[ast_grep.py]
    COL --> CO3[git_log.py · docs_reader.py]
    COL --> CO4[orchestrator.py]

    ROOT --> FIS[file_selector.py]

    ROOT --> ADA[adapters/]
    ADA --> A1[base.py]
    ADA --> A2[rules.py · summary.py]
    ADA --> A3[orchestrator.py]

    ROOT --> PRO[providers/]
    PRO --> P1[claude.py · codex.py]

    ROOT --> PRM[prompts/templates/]
    PRM --> T1[extract_rules_python.md<br>extract_rules_ts.md<br>extract_rules.md]
    PRM --> T2[summary_python.md<br>summary_ts.md<br>summary.md]

    ROOT --> SCH[schemas/ · storage/ · utils/]
```

---

## 5. AnalysisContext Data Model

```mermaid
classDiagram
    class AnalysisContext {
        ArchitectureSnapshot architecture
        dict patterns
        GitPatternsSnapshot git_patterns
        dict docs
    }
    class ArchitectureSnapshot {
        list~FileScore~ file_scores
        list~CouplingPair~ coupling_pairs
    }
    class FileScore {
        str path
        float churn
        int age
        float centrality
    }
    class CouplingPair {
        str file_a
        str file_b
        int degree
    }
    class GitPatternsSnapshot {
        list hotspots
        list stable_files
        list coupling_clusters
    }

    AnalysisContext *-- ArchitectureSnapshot
    AnalysisContext *-- GitPatternsSnapshot
    ArchitectureSnapshot *-- FileScore
    ArchitectureSnapshot *-- CouplingPair
```
