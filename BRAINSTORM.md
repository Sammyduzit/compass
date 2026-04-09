# Compass — Team Brainstorming Guide

> **Purpose of this document:** Prepare the team for a productive first brainstorming session.
>
> Before the session: read `DECIDED.md` (what's locked) and `VISIONS.md` (what we're building). Then read this document.
>
> The session goal is not to produce answers. It's to produce **the right questions** — questions that, when answered well, make the implementation decisions obvious.

---

## How to brainstorm well

Good brainstorming is not generating ideas randomly. It's a structured process of:

1. **Understand the constraint** — what problem are we actually solving?
2. **Map the unknowns** — what do we not know yet that matters?
3. **Generate options** — what are the different ways this could work?
4. **Identify trade-offs** — what does each option cost and what does it gain?
5. **Make a decision or escalate** — either decide, or identify what information you'd need to decide

For each topic below: don't stop at "here's an idea." Push to "here's the trade-off between option A and option B, and here's what would make us choose one over the other."

**AI as a brainstorming partner:** You can use Claude (or any AI) to explore options — but your job is to *drive* the conversation, not follow wherever it leads. The AI will generate ideas; you decide which ones are worth pursuing and why. A good prompt to start: *"I'm trying to decide between [option A] and [option B] for [context]. What are the trade-offs? What am I missing?"*

---

## Topics for the session

### 1. How do we measure output quality?

The tool produces `rules.yaml` and `summary.md`. But how do we know if the output is good?

- What does "good" mean for a rules file? What does "bad" mean?
- Could two people run the tool on the same repo and get meaningfully different results? Is that a problem?
- How do we test quality during development without manually reviewing every run?
- What would a "golden example" look like — an output we could compare against?

> **Why this matters:** If we can't measure quality, we can't improve it. This question affects how we design the prompts, how we build test cases, and how we know when v1 is "done enough" to ship.

---

### 2. What goes into the AnalysisContext?

The AnalysisContext is the persisted JSON that all adapters read from. Its schema is not yet defined.

- What information does a `rules.yaml` adapter actually need from the codebase?
- What information does a `summary.md` adapter need? Is it different?
- How much is too much? (More context = higher LLM cost per adapter call)
- How much is too little? (Missing context = lower quality output)
- Should collectors run in parallel or sequentially? Does order matter?

> **Why this matters:** The AnalysisContext schema is the contract between Phase 1 and Phase 2. Getting it wrong means either re-collecting data or missing information. Getting it right means adapters are independent and fast.

---

### 3. How do we handle repos that don't fit the expected pattern?

The current pipeline was designed and tested against one TypeScript/Node.js repo with a layered architecture.

- What happens on a Python monolith? A Go microservice? A Django app?
- What happens on a 5-file hobby project vs. a 2000-file enterprise repo?
- What happens when there's no git history? No tests? No clear architecture?
- Should the tool fail gracefully, warn the user, or try to adapt?

> **Why this matters:** If the tool only works on a specific kind of codebase, it's not a general tool — it's a script. Understanding the failure modes early shapes the design of the collectors and prompts.

---

### 4. What is the developer experience of running this tool?

Imagine you're a new intern at a company. You clone their repo. What do you actually want?

- What's the first thing you'd want to know about the codebase?
- What output format is actually useful to you? (YAML? Markdown? Both?)
- How long is "too long" for the tool to run? (1 min? 5 min? 10 min?)
- What would make you trust the output? What would make you distrust it?

> **Why this matters:** We're building this for a specific user. Thinking from their perspective catches usability problems before they're built in.

---

### 5. What does a good prompt look like?

The quality of the LLM output depends almost entirely on the prompt.

- What information should the prompt include about the codebase?
- How do we prevent hallucinations? (The v0 pipeline had one hallucinated rule.)
- Should the prompt be different for different repo types/languages?
- How do we structure the prompt so the LLM produces valid, schema-conforming output?
- How do we iterate on prompts efficiently — without re-running the full pipeline each time?

> **Why this matters:** Prompts are the core logic of the adapters. A bad prompt produces bad output regardless of how good the surrounding code is.

---

### 6. What's the right scope for v1?

`DECIDED.md` says v1 ships two adapters: RulesAdapter and SummaryAdapter. But there are still open questions within that scope.

- What is the minimum viable version of each adapter that is still useful?
- Should v1 support multiple languages, or just TypeScript/Node first?
- Should prerequisites auto-check be in v1, or is manual setup acceptable for the first version?
- What does "done" mean for v1? Who decides?

> **Why this matters:** Scope creep kills projects, especially with distributed teams. Being explicit about what v1 is — and is not — keeps everyone aligned.

---

## How to use this in the session

1. **Before the session:** Each person picks 1–2 topics and prepares their thoughts (what they know, what they don't know, what questions they have).
2. **In the session:** For each topic, start with the constraint (the "why this matters" box), then explore options and trade-offs. Use the AI to stress-test ideas.
3. **Output of the session:** For each topic, either:
   - A decision (add it to `DECIDED.md`)
   - A question that needs more research (add it as a GitHub issue)
   - A question that needs a prototype to answer (add it as a ticket)

The goal is not a perfect plan. It's a list of decisions and a list of what we still need to figure out.
