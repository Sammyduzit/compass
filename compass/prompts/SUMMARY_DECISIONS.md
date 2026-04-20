# Prompts & Quality — Decisions Log

> **Owner:** Stuart McLean (Team 4)
> **Status:** Final — these decisions are reflected in the prompt templates and schemas
> **Affects:** Adapters team (summary_schema.py implementation), CLI team (--depth v2)

---

## Decision 1 — `summary.json` generated alongside `summary.md`

**Decision:** SummaryAdapter generates both `summary.json` and `summary.md` in
the same single LLM call. No additional call required.

**Reason:** The JSON is the data layer; the markdown is one rendering of it.
Generating JSON now costs nothing — the LLM is already producing the structured
content. Retrofitting it later requires writing a markdown parser to reconstruct
information that was always available in the pipeline. That is wasted work, and
it closes the door on a UI layer that the UX brief argued for explicitly.

**What this means for the Adapters team:**
`summary_schema.py` must validate the JSON structure, not just the markdown.
The full JSON schema is defined in `prompts/templates/summary.md` under
"JSON Output". Implement `summary_schema.py` against that schema.

**What the JSON schema looks like:**
```json
{
  "repo_name": "string",
  "generated_at": "ISO 8601 timestamp",
  "what_it_does": "string",
  "read_first": [
    { "path": "string", "reason": "string" }
  ],
  "stable": [
    { "path": "string", "note": "string" }
  ],
  "hotspots": [
    { "path": "string", "note": "string" }
  ],
  "clusters": [
    {
      "id": "integer",
      "summary": "string",
      "files": ["string"],
      "coupling_pairs": [["string", "string"]]
    }
  ]
}
```

Empty arrays `[]` are valid for any list field. No field may be omitted.

---

## Decision 2 — `--depth` flag deferred to v2

**Decision:** No `--depth shallow|standard|deep` flag in v1. The flag was
proposed in the SummaryAdapter brainstorm but is not in the locked CLI in
FINAL.md.

**Reason:** Adding it to v1 touches the CLI, runner, adapter interface, and
prompt template. It also opens questions about whether the JSON schema changes
per depth level. One well-structured output is better than three depth variants
for v1.

**How the template handles depth without a flag:**
Sections are ordered from orientation to depth. A junior developer reads
top-to-bottom. A senior skips to what they need. The structure does the
adaptation work — no flag required.

**For v2:** the template is designed so `--depth` can be added as a parameter
without restructuring the output. The sections already map cleanly to
shallow (sections 1–2), standard (sections 1–4), and deep (all five). Flag
this when planning v2 scope.

---

## Reference

These decisions were made in response to Sam's direction: "you own both sides
of it (template structure + validation strictness). Just document what you
decide, since the Adapters will implement summary_schema.py based on whatever
you land on."

Full rationale in `research/UX_BRIEF_final.md` and
`research/SUMMARY_ADAPTER__brainstorm_.md`.
