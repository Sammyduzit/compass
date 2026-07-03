import type { SummaryData, RulesData } from '../types'

export const mockSummary: SummaryData = {
  repo_name: 'compass',
  generated_at: '2026-05-04T10:00:00Z',
  what_it_does:
    'Compass is a CLI pipeline tool that scans an unfamiliar codebase and produces structured artifacts — rules.yaml and summary.md — to help developers onboard fast. It extracts conventions and architectural patterns from actual code using a two-phase port-adapter architecture: a data collection phase with no LLM costs, followed by focused LLM adapter calls that produce structured outputs.',
  read_first: [
    {
      path: 'compass/runner.py',
      reason: 'The orchestration layer — understand this and you understand how the whole pipeline fits together.',
    },
    {
      path: 'compass/adapters/summary.py',
      reason: 'Shows the full adapter pattern: file selection, skeleton rendering, LLM call, output writing.',
    },
    {
      path: 'compass/collectors/base.py',
      reason: 'Base class that every collector extends — defines the async contract for Phase 1.',
    },
    {
      path: 'compass/schemas/summary_schema.py',
      reason: 'Locked output schema for summary.json — the contract between the CLI and the UI.',
    },
  ],
  stable: [
    { path: 'compass/collectors/base.py', note: 'Abstract base, low churn — safe to copy patterns from.' },
    { path: 'compass/schemas/', note: 'Locked schemas — deliberately stable, changes here are breaking.' },
    { path: 'compass/cli.py', note: 'Thin wrapper over runner.py — intentionally minimal and stable.' },
  ],
  hotspots: [
    {
      path: 'compass/adapters/summary.py',
      note: 'Actively evolving — prompt template and JSON extraction logic still being refined.',
    },
    {
      path: 'compass/collectors/file_selector.py',
      note: 'Per-adapter file selection is being tuned — apply_coverage() logic changes frequently.',
    },
  ],
  clusters: [
    {
      id: 1,
      summary:
        'The collector stack gathers all signals in Phase 1 with zero LLM cost. CollectorBase defines the async contract; each collector implements it independently. They always run together to produce a complete AnalysisContext.',
      files: [
        'compass/collectors/base.py',
        'compass/collectors/git_collector.py',
        'compass/collectors/ast_grep_collector.py',
        'compass/collectors/import_graph_collector.py',
      ],
      coupling_pairs: [
        ['compass/collectors/base.py', 'compass/collectors/git_collector.py'],
        ['compass/collectors/base.py', 'compass/collectors/import_graph_collector.py'],
      ],
    },
    {
      id: 2,
      summary:
        'The adapter layer runs one focused LLM call per output. FileSelector and skeleton rendering happen at Phase 2 runtime — each adapter selects only the files it needs. Adapters are independent and re-runnable without re-collecting.',
      files: [
        'compass/adapters/summary.py',
        'compass/adapters/rules.py',
        'compass/file_selector.py',
        'compass/skeleton.py',
      ],
      coupling_pairs: [
        ['compass/adapters/summary.py', 'compass/skeleton.py'],
        ['compass/adapters/rules.py', 'compass/file_selector.py'],
      ],
    },
    {
      id: 3,
      summary:
        'Runner and CLI form the entry point separation. cli.py is a thin argument parser that calls Runner. runner.py owns all pipeline logic and knows nothing about the CLI — this separation is what makes the FastAPI layer possible without a refactor.',
      files: ['compass/cli.py', 'compass/runner.py'],
      coupling_pairs: [['compass/cli.py', 'compass/runner.py']],
    },
  ],
}

export const mockRules: RulesData = {
  clusters: [
    {
      name: 'Collector Pattern',
      context:
        'All Phase 1 data collection follows the async collector pattern. Collectors never call LLMs — they gather signals only.',
      golden_file: 'compass/collectors/base.py',
      rules: [
        {
          id: 'col-01',
          rule: 'Every collector must extend CollectorBase and implement the async collect() method.',
          why: 'Ensures Runner can await all collectors uniformly without knowing their implementation details.',
          example: 'class GitCollector(CollectorBase):\n    async def collect(self) -> dict:\n        ...',
        },
        {
          id: 'col-02',
          rule: 'Collectors must never call LLMs or make network requests beyond the target repo.',
          why: 'Phase 1 must be zero-LLM-cost and deterministic. LLM calls belong in adapters.',
          example: '# Wrong: calling an LLM inside a collector\n# Right: return raw git log output for adapters to interpret',
        },
        {
          id: 'col-03',
          rule: 'Collector output is merged into AnalysisContext and persisted to .compass/analysis_context.json.',
          why: 'Persistence means Phase 1 runs once. Adapters re-run cheaply without re-collecting.',
          example: 'context.architecture = await import_graph_collector.collect()',
        },
      ],
    },
    {
      name: 'Adapter Pattern',
      context:
        'Phase 2 adapters each make one focused LLM call. They are independent, re-runnable, and output to .compass/output/.',
      golden_file: 'compass/adapters/summary.py',
      rules: [
        {
          id: 'adp-01',
          rule: 'Each adapter makes exactly one LLM call. Multiple calls per adapter are not permitted in v1.',
          why: 'Keeps cost predictable and each adapter independently re-runnable.',
          example: 'response = await self._llm.call(prompt)  # one call, one output',
        },
        {
          id: 'adp-02',
          rule: 'Adapters raise AdapterError for all failure conditions — never let raw exceptions propagate to Runner.',
          why: 'Runner catches AdapterError to report cleanly. Unhandled exceptions crash the whole pipeline.',
          example: 'except SkeletonError as exc:\n    raise AdapterError(self.name, str(exc)) from exc',
        },
        {
          id: 'adp-03',
          rule: 'File selection and skeleton rendering happen at adapter runtime, not stored in AnalysisContext.',
          why: 'Skeletons are large and adapter-specific. Storing them would bloat the context and couple adapters.',
          example: 'selected = select_files(context, CRITERIA, lang)\nskeletons = render_skeletons(abs_paths)',
        },
      ],
    },
    {
      name: 'Error Handling',
      context:
        'Errors surface cleanly at each layer boundary. The orchestrator catches AdapterError; adapters catch everything below them.',
      golden_file: 'compass/adapters/base.py',
      rules: [
        {
          id: 'err-01',
          rule: 'Wrap all external tool calls (grep_ast, repomix, ast-grep) in try/except and re-raise as AdapterError.',
          why: 'External tools have unpredictable failure modes. The adapter layer is where those get normalised.',
          example:
            'try:\n    result = render_skeletons(files)\nexcept SkeletonError as exc:\n    raise AdapterError(self.name, str(exc)) from exc',
        },
        {
          id: 'err-02',
          rule: 'Validation failures trigger one retry before raising SchemaValidationError.',
          why: 'LLM output is non-deterministic. One retry catches transient formatting errors without masking real failures.',
          example: 'for attempt in range(2):\n    response = await self._llm.call(prompt)\n    if validate(response): break',
        },
      ],
    },
  ],
}
