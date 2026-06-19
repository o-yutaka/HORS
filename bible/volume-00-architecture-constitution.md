# Volume 00 — HROS Architecture Constitution

**Document ID:** `bible/volume-00-architecture-constitution.md`  
**System:** HROS — HERMES Research Operating System  
**Version:** 1.0.0  
**Status:** Ratified  
**Authority:** Supreme architectural law for all HROS artifacts  

---

## Table of Contents

1. [Preamble](#1-preamble)
2. [Scope and Definitions](#2-scope-and-definitions)
3. [Architectural Principles](#3-architectural-principles)
4. [Tier Architecture](#4-tier-architecture)
5. [Dependency Rules](#5-dependency-rules)
6. [Repository Topology](#6-repository-topology)
7. [Prompt Assembly Tiers](#7-prompt-assembly-tiers)
8. [Evolution Rules](#8-evolution-rules)
9. [ADR Governance](#9-adr-governance)
10. [RFC Process](#10-rfc-process)
11. [Stability Matrix](#11-stability-matrix)
12. [Promotion and Deprecation](#12-promotion-and-deprecation)
13. [Observability and Logs](#13-observability-and-logs)
14. [Compliance and Enforcement](#14-compliance-and-enforcement)
15. [Amendment Procedure](#15-amendment-procedure)
16. [Appendix A — Tier Dependency Diagram](#appendix-a--tier-dependency-diagram)
17. [Appendix B — Change-Class Quick Reference](#appendix-b--change-class-quick-reference)

---

## 1. Preamble

HROS is a **research operating system** for autonomous and semi-autonomous agents that conduct, document, and evolve scientific and engineering research. It is not a single application. It is a **layered constitution of capabilities**, bound together by explicit dependency law, stability contracts, and governed change.

This Volume 00 document is the **root authority**. No RFC, ADR, implementation, prompt, or experiment may contradict an active clause herein. When conflict arises, this constitution prevails until formally amended.

The name **HERMES** denotes the agent lineage and operational philosophy: message-bearing intelligence that learns, remembers, and routes work across sessions. **HROS** denotes the **operating system envelope**—kernel, capabilities, services, infrastructure, and workspace—that hosts that intelligence under reproducible rules.

---

## 2. Scope and Definitions

### 2.1 Scope

This constitution governs:

- All directories at the HROS repository root listed in [Section 6](#6-repository-topology)
- All code, configuration, prompts, and documentation placed within those directories
- All promotion paths from `experiments/` into production tiers
- All architecture decisions recorded in `adr/`

This constitution does **not** govern external upstream projects (model weights, third-party gateways, user-owned workspace content) except where HROS integrates with them via defined ports.

### 2.2 Definitions

| Term | Definition |
|------|------------|
| **Tier** | An architectural stratum with fixed dependency privileges and stability class |
| **Artifact** | Any file, module, service, prompt template, or schema under HROS |
| **Port** | A declared interface in `core/` that lower tiers implement or higher tiers consume |
| **Capability** | An atomic, tool-addressable unit of agent action registered in `capability/` |
| **Service** | A composed workflow in `service/` that orchestrates multiple capabilities |
| **Kernel** | The runtime loop in `kernel/` that schedules turns, tools, and session lifecycle |
| **Workspace** | Per-project research context in `workspace/` (context files, local state, artifacts) |
| **Stable prefix** | Prompt and runtime content intended to remain fixed for the duration of a session |
| **Volatile surface** | Session-scoped content that may change every turn without violating stability contracts |
| **ADR** | Architecture Decision Record — binding decision artifact in `adr/` |
| **RFC** | Request for Comments — proposal artifact in `rfc/` preceding material change |
| **Promotion** | Controlled movement of an artifact from `experiments/` into a production tier |
| **Breaking change** | Any change that invalidates a port contract, ADR guarantee, or stability matrix row |

---

## 3. Architectural Principles

All HROS design must uphold these principles. They are non-negotiable unless this constitution is amended.

### P1 — Constitution First

Architecture is law, not commentary. Implementations follow ratified structure; structure does not follow expedient implementations.

### P2 — Downward Dependencies Only

Higher tiers consume lower tiers. Reverse dependencies are forbidden except through explicit port inversion documented in an ADR.

### P3 — Cache-Friendly Stability

Stable identity, guidance, and contracts are separated from volatile session data. Mid-session mutation of stable surfaces is prohibited unless a ratified rebuild path runs (compression, session boundary, explicit invalidation).

### P4 — Capabilities Are Atomic

A capability does one coherent job, exposes a narrow contract, and fails loudly. Services compose; capabilities do not orchestrate peer capabilities.

### P5 — Research Is Reproducible

Every material action emits auditable evidence in `logs/`. Experiments must declare hypotheses, inputs, and evaluation criteria before promotion is considered.

### P6 — Governed Evolution

No silent architecture drift. Material changes traverse RFC → review → ADR → implementation. Emergency fixes are allowed but must be retro-documented within one release cycle.

### P7 — Workspace Sovereignty

User and project context in `workspace/` overrides default agent behavior where constitution permits, but never overrides safety boundaries defined in Tier 0 and ratified ADRs.

### P8 — Fail Closed

Ambiguous permissions, unknown tool schemas, or unresolved dependency edges must deny execution rather than guess.

---

## 4. Tier Architecture

HROS runtime architecture is organized into **nine numbered tiers** plus one **experimental sandbox**. Tiers are ordered by **dependency rank**: lower number = more foundational = fewer upstream consumers.

### Tier 0 — Constitution (`bible/`)

**Role:** Canonical law, volumes, glossaries, and ratified architectural scripture.  
**Contains:** This document and subsequent bible volumes.  
**May depend on:** Nothing in the repository.  
**Consumed by:** Humans, agents, and governance processes (not runtime import graphs).

### Tier 1 — Kernel (`kernel/`)

**Role:** Agent loop, turn scheduler, session lifecycle, tool dispatch, compression and rebuild triggers.  
**Contains:** `AIAgent` loop equivalents, session store bindings, provider runtime resolution hooks.  
**May depend on:** Tier 2 (`core/`) ports and kernel-internal modules only.  
**Must not depend on:** Capability, service, infrastructure implementations, workspace content, experiments.

### Tier 2 — Core (`core/`)

**Role:** Shared types, protocols, port definitions, error taxonomy, identity of research objects.  
**Contains:** Interface definitions, schema registries, cross-tier contracts.  
**May depend on:** Tier 2 only (internal cohesion).  
**Must not depend on:** Kernel orchestration logic, concrete adapters, workspace files.

### Tier 3 — Capability (`capability/`)

**Role:** Atomic tools and skills-facing executors (file, browser, terminal, memory read/write, etc.).  
**Contains:** Tool handlers, capability metadata, registration descriptors.  
**May depend on:** Tier 2 ports; Tier 1 dispatch interfaces (types only, not loop control).  
**Must not depend on:** Services, other capabilities' private modules, workspace-specific paths hardcoded.

### Tier 4 — Service (`service/`)

**Role:** Multi-step workflows: research pipelines, batch evaluation, gateway-facing orchestration.  
**Contains:** Service modules that sequence capabilities with policy.  
**May depend on:** Tier 3, Tier 2.  
**Must not depend on:** Infrastructure concrete drivers (must use ports).

### Tier 5 — Infrastructure (`infrastructure/`)

**Role:** Adapters for storage, messaging gateways, provider backends, sandboxes, credentials passthrough.  
**Contains:** SQLite stores, gateway bridges, env passthrough, terminal backends.  
**May depend on:** Tier 2 ports; implements ports defined in core.  
**Must not depend on:** Service orchestration, capability business logic.

### Tier 6 — Workspace (`workspace/`)

**Role:** Per-research-project envelope: context files, local indexes, run artifacts, HERMES-style project law.  
**Contains:** Project templates, workspace loaders, context file resolution (`.hermes.md`, `AGENTS.md`, etc.).  
**May depend on:** Tier 2, Tier 4 service **interfaces** (not private implementations).  
**Must not depend on:** Experiments; must not embed kernel loop code.

### Tier 7 — Prompts (`prompts/`)

**Role:** Prompt templates, assembly rules, and tiered prompt libraries (stable / context / volatile guidance).  
**Contains:** SOUL templates, skills prompt fragments, assembly documentation.  
**May depend on:** Tier 2 schema for prompt slots; references workspace resolution rules from Tier 6.  
**Must not depend on:** Concrete infrastructure providers.

### Tier E — Experiments (`experiments/`)

**Role:** Sandbox for hypotheses not yet bound by stability contracts.  
**Contains:** Prototypes, ablations, one-off runners, draft capabilities.  
**May depend on:** Any production tier for evaluation purposes.  
**Protected by:** Nothing in Tiers 0–7 may depend on Tier E.

### Governance Plane (orthogonal)

| Path | Role |
|------|------|
| `rfc/` | Pre-decision proposals and design debate |
| `adr/` | Ratified, binding architecture decisions |
| `logs/` | Audit trails, run evidence, promotion records |

The governance plane does not participate in runtime dependency ranking but constrains all tiers.

---

## 5. Dependency Rules

### 5.1 Master Rule

> **A module at Tier T may import only modules at Tier ≤ T (within production tiers 0–7), and only along allowed edges defined below.**

Tier 0 is non-importable. Tier E is import-only (others may read experiments for evaluation; experiments may read production).

### 5.2 Allowed Dependency Edges

| From Tier | May Import |
|-----------|------------|
| 1 Kernel | 2 Core |
| 2 Core | 2 Core |
| 3 Capability | 2 Core, 1 Kernel **types/interfaces** |
| 4 Service | 3 Capability, 2 Core |
| 5 Infrastructure | 2 Core (implements ports) |
| 6 Workspace | 2 Core, 4 Service interfaces |
| 7 Prompts | 2 Core, 6 Workspace rules |
| E Experiments | 1–7 (read/evaluate) |

### 5.3 Forbidden Dependency Patterns

The following are **architectural violations**:

1. **Upward import:** e.g., `core/` importing `service/`
2. **Sideways intimacy:** `capability/` importing another capability's private implementation (use shared `core/` or a service)
3. **Kernel bypass:** capabilities invoking provider APIs without kernel dispatch
4. **Infrastructure leakage:** `infrastructure/` calling `service/` or `capability/` directly
5. **Experiment contamination:** any Tier 0–7 production module importing `experiments/`
6. **Constitution coupling:** runtime code parsing `bible/` for behavioral logic (human/agent governance only)
7. **Circular port graphs:** any cycle among `core/` port definitions
8. **Volatile-in-stable:** embedding session timestamps, memory snapshots, or user profile data in Tier 7 stable templates

### 5.4 Port Inversion Exception

When a lower tier must notify a higher tier (e.g., infrastructure event → service), use:

1. A port defined in Tier 2 (`core/`)
2. Registration at startup by the higher tier
3. An ADR documenting the inversion and lifecycle

Ad-hoc callbacks across tiers without ports are forbidden.

### 5.5 Dependency Verification

Before merge to any Tier 1–7 path:

- Static import analysis must confirm allowed edges
- CI dependency graph check must pass (no new forbidden edges)
- ADR required if any new cross-tier edge is introduced

---

## 6. Repository Topology

The HROS root layout is **normative**. New top-level directories require a constitution amendment or ratified ADR with amendment-equivalent authority.

```
HROS/
├── bible/              # Tier 0 — Constitution and volumes
├── adr/                # Governance — Architecture Decision Records
├── rfc/                # Governance — Requests for Comments
├── prompts/            # Tier 7 — Prompt libraries and assembly
├── core/               # Tier 2 — Ports, types, protocols
├── kernel/             # Tier 1 — Agent loop and lifecycle
├── capability/       # Tier 3 — Atomic capabilities
├── service/            # Tier 4 — Composed services
├── infrastructure/   # Tier 5 — Adapters and gateways
├── workspace/        # Tier 6 — Project workspace envelope
├── experiments/        # Tier E — Sandbox
├── logs/               # Observability — audit and run evidence
└── README.md           # Entry index (non-authoritative; points to bible/)
```

`README.md` is an index, not law. If `README.md` disagrees with this volume, this volume wins.

---

## 7. Prompt Assembly Tiers

Prompt content follows a **three-layer assembly model** inside Tier 7 (`prompts/`), aligned with kernel session caching policy.

### 7.1 Assembly Order

Final system prompt join order:

```
stable → context → volatile
```

### 7.2 Layer Definitions

| Layer | Stability | Contents | Rebuild Policy |
|-------|-----------|----------|----------------|
| **stable** | Session-fixed | Identity (SOUL), tool/model guidance, skills prompt skeleton, environment hints | Rebuild only at session start or ratified invalidation |
| **context** | Session-fixed | Project context files, caller `system_message`, workspace-resolved law | Rebuild only at session start or context file change + invalidation |
| **volatile** | Per-turn | Memory snapshot, user profile, external memory block, timestamp/session line | May change each turn **only** via volatile channel APIs, never by mutating cached stable/context |

### 7.3 Context File Priority

Workspace resolution uses **first match wins** (only one project context type loaded):

1. `.hermes.md` / `HERMES.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `.cursorrules`

Documented in ADR when extended.

### 7.4 Prohibited Mid-Session Mutations

These must not be reinjected into the cached system prompt mid-session:

- Ephemeral system prompt fragments
- Prefill-derived session context in stable layer
- Hon-style compaction summaries into stable layer
- Ad-hoc memory writes reflected in stable/context without rebuild

Separation preserves provider prefix caching and predictable memory semantics.

---

## 8. Evolution Rules

### 8.1 Change Classes

| Class | Description | Typical Path |
|-------|-------------|--------------|
| **C0 — Editorial** | Typos, non-normative clarifications in bible | Direct commit to bible with review |
| **C1 — Local** | Internal refactor, no port/ADR change | PR + tests |
| **C2 — Contract** | Port, schema, or behavior contract change | RFC → ADR → PR |
| **C3 — Structural** | New tier, new top-level directory, dependency edge | RFC → ADR → constitution amendment |
| **C4 — Emergency** | Production-breaking fix | Fix → retro RFC/ADR within 14 days |

### 8.2 Standard Evolution Pipeline

```
Hypothesis (experiments/) → RFC (rfc/) → Review → ADR (adr/) → Implementation → Logs (logs/)
```

1. **Experiment** — Demonstrate need with reproducible evidence in `experiments/` and `logs/`
2. **RFC** — Propose design, alternatives, migration, rollback
3. **Review** — Minimum one architectural reviewer; C2/C3 require two
4. **ADR** — Ratify decision; link RFC; state status
5. **Implement** — Change only tiers named in ADR
6. **Record** — Promotion and deployment evidence in `logs/`

### 8.3 Versioning

- **Constitution:** Semantic version on this file (`Version:` header)
- **Ports (core/):** Semantic versioning per port package; breaking = major
- **Capabilities:** Capability ID is stable; breaking handler contract = new capability ID or ADR-approved migration window
- **Services:** Service API version in metadata; consumers declare compatibility

### 8.4 Backward Compatibility

- **Default:** Maintain backward compatibility for one minor release cycle after deprecation notice
- **Breaking changes:** Require ADR, migration guide, and stability matrix update
- **Deprecation:** ADR status `deprecated` with successor ADR link

### 8.5 Experiment Lifecycle

| State | Location | Rule |
|-------|----------|------|
| Draft | `experiments/` | No production dependency |
| Evaluated | `experiments/` + `logs/` | Metrics attached |
| Proposed | `rfc/` | Promotion RFC open |
| Ratified | `adr/` + target tier | Promotion complete |
| Abandoned | `experiments/` archived | ADR or RFC marked withdrawn |

Maximum experiment lifetime without RFC: **90 days**, then archive or extend via RFC.

---

## 9. ADR Governance

### 9.1 Purpose

ADRs are the **binding decision ledger**. They explain *why* the architecture is shaped as it is and what invariants implementations must uphold.

### 9.2 ADR File Convention

```
adr/NNNN-short-title.md
```

- `NNNN` — zero-padded sequence (e.g., `0001`, `0042`)
- `short-title` — lowercase kebab-case
- One decision per ADR; supersession chains via links

### 9.3 Required ADR Template

Every ADR must contain:

```markdown
# ADR-NNNN: Title

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Date
YYYY-MM-DD

## Context
What forces, constraints, or problems apply?

## Decision
What was decided?

## Consequences
Positive, negative, and neutral outcomes.

## Compliance
How will adherence be verified?

## Links
- RFC: rfc/...
- Supersedes: ADR-...
- Related: ADR-...
```

### 9.4 Status Transitions

| From | To | Requirement |
|------|-----|-------------|
| Proposed | Accepted | Review complete; no open blocking RFC objections |
| Accepted | Deprecated | Successor or migration ADR identified |
| Accepted | Superseded | New ADR explicitly lists superseded ADR |
| Proposed | Rejected | Document reason in ADR + close RFC |

### 9.5 When an ADR Is Mandatory

An ADR is **required** for:

- Any C2 or C3 change ([Section 8.1](#81-change-classes))
- New capability registration that exposes external side effects
- New infrastructure adapter with credential or network access
- New dependency edge ([Section 5](#5-dependency-rules))
- Prompt assembly rule changes affecting stable/context boundaries
- Security boundary changes

### 9.6 ADR Authority Relative to Constitution

- ADRs **cannot override** Tier 0 constitution
- ADRs **can** refine implementation detail within constitutional bounds
- Conflicting Accepted ADRs are resolved by supersession, not silent merge

### 9.7 ADR Index

Maintain `adr/README.md` as a table of all ADRs with status and tier impact. Index updates are C0/C1 unless reclassification occurs.

---

## 10. RFC Process

RFCs precede material ADRs. They are the **debate surface**; ADRs are the **verdict**.

### 10.1 RFC File Convention

```
rfc/NNNN-short-title.md
```

Numbering namespace is independent of ADR numbering but should cross-reference.

### 10.2 RFC Template

```markdown
# RFC-NNNN: Title

## Summary
One paragraph.

## Motivation
Why now?

## Proposal
Detailed design.

## Alternatives Considered
Including do-nothing.

## Tier Impact
Which tiers change?

## Dependency Impact
New edges? Port changes?

## Migration and Rollback
Step-by-step.

## Experiment Evidence
Links to experiments/ and logs/

## Open Questions
```

### 10.3 RFC Lifecycle

1. **Draft** — Author opens RFC in `rfc/`
2. **Review** — Minimum 5 business days for C2, 10 for C3
3. **Accepted** — Convert to ADR; RFC header links to ADR
4. **Rejected** — Status updated; reason recorded
5. **Withdrawn** — Author withdraws without rejection stigma

RFC acceptance does not imply implementation; ADR acceptance does.

---

## 11. Stability Matrix

The stability matrix assigns **change velocity, approval gates, and test obligations** per tier and governance path.

### 11.1 Tier Stability Matrix

| Tier | Path | Stability Class | Change Velocity | Approval Gate | Breaking Change Policy | Test Requirement |
|------|------|-----------------|-----------------|---------------|------------------------|-------------------|
| 0 | `bible/` | **Immutable law** | Months/years | Amendment procedure ([§15](#15-amendment-procedure)) | Forbidden without amendment | N/A (document review) |
| 1 | `kernel/` | **Critical** | Weeks | RFC + ADR + 2 reviewers | One major cycle deprecation | Loop integration + regression suite |
| 2 | `core/` | **High** | Weeks | RFC + ADR | Versioned ports; major bump | Contract tests for all ports |
| 3 | `capability/` | **Medium** | Days–weeks | ADR for external effects | New ID or migration ADR | Capability unit + sandbox tests |
| 4 | `service/` | **Medium** | Days–weeks | ADR for new service | Service version bump | Workflow integration tests |
| 5 | `infrastructure/` | **High** | Weeks | ADR for new adapter class | Adapter version bump | Adapter contract + integration |
| 6 | `workspace/` | **Medium-low** | Days | ADR for resolution rule changes | Template migration guide | Workspace loader tests |
| 7 | `prompts/` | **Split** | Days–weeks | ADR for stable/context boundary changes | Stable layer versioning | Prompt assembly snapshot tests |
| E | `experiments/` | **None** | Hourly | Author discretion | No guarantee | Best-effort; evidence required for promotion |

### 11.2 Governance Stability Matrix

| Path | Stability Class | Approval Gate | Retention |
|------|-----------------|---------------|-----------|
| `rfc/` | Provisional | Review period | Permanent history |
| `adr/` | Binding | ADR acceptance | Permanent; supersession chain |
| `logs/` | Append-only | Automatic | Per retention ADR; default 1 year run logs |

### 11.3 Prompt Layer Stability Matrix

| Layer | Stability Class | Mid-Session Mutation | Rebuild Trigger |
|-------|-----------------|----------------------|-----------------|
| stable | Critical | **Forbidden** | Session start, compression rebuild, explicit invalidation ADR |
| context | High | **Forbidden** | Session start, context file change + invalidation |
| volatile | Low | **Allowed** | Per-turn via volatile APIs only |

### 11.4 Stability vs. Dependency

Higher stability class implies **stricter** change gates, not necessarily lower tier number. Tier 1 kernel and Tier 2 core are both Critical/High stability despite adjacent ranks.

---

## 12. Promotion and Deprecation

### 12.1 Promotion Checklist (Experiments → Production)

Before an artifact leaves `experiments/`:

- [ ] Experiment ID and hypothesis documented
- [ ] Evaluation logs in `logs/` with reproducible inputs
- [ ] RFC reviewed and linked
- [ ] ADR Accepted with target tier and module path
- [ ] Dependency graph check passes
- [ ] Stability matrix row for target tier satisfied (tests, reviewers)
- [ ] No remaining imports from `experiments/` in production code
- [ ] Promotion record appended to `logs/promotions/`

### 12.2 Deprecation Checklist

- [ ] ADR updated to `Deprecated` with date and successor
- [ ] Migration guide published
- [ ] Compatibility window started per [§8.4](#84-backward-compatibility)
- [ ] Telemetry or logs confirm low usage before removal

---

## 13. Observability and Logs

### 13.1 Purpose

`logs/` is the **evidence layer**. Research operating systems must be auditable.

### 13.2 Required Log Classes

| Class | Contents |
|-------|----------|
| `logs/runs/` | Session/run identifiers, tier, capability invocations |
| `logs/promotions/` | Experiment promotion and ADR linkage |
| `logs/audits/` | Security-relevant denials, credential access |
| `logs/evals/` | Benchmark and experiment metrics |

### 13.3 Log Integrity

- Append-preferred; tamper-evident hashing recommended (ADR for implementation)
- Logs are not imported by kernel loop in hot path (async emitters only)
- Retention and PII policy defined by ADR

---

## 14. Compliance and Enforcement

### 14.1 Automated Enforcement

CI must enforce:

1. Dependency rule violations ([§5](#5-dependency-rules))
2. Missing ADR for forbidden change classes
3. Stability matrix test tiers per touched path
4. Prompt assembly snapshot drift for stable layer

### 14.2 Human Enforcement

Architectural reviewers block merge on:

- Unresolved RFC objections for C2/C3
- Constitution contradiction
- Experiment contamination

### 14.3 Agent Enforcement

Agents operating in HROS must:

1. Read Tier 0 before structural changes
2. Propose RFC before C2/C3 implementation
3. Never commit production imports from `experiments/`
4. Emit run evidence for material capability executions

---

## 15. Amendment Procedure

### 15.1 Constitution Amendments

Amending this Volume 00 requires:

1. RFC with `Tier Impact: Tier 0` and explicit clause diffs
2. ADR with status Accepted and title prefix `Constitution Amendment`
3. Version bump on this document's `Version:` header
4. Changelog entry in `bible/CHANGELOG.md` (created on first amendment)

### 15.2 Minor vs. Major Amendments

| Type | Examples | Process |
|------|----------|---------|
| **Minor** | Clarifications, glossary, non-normative examples | RFC + ADR + 1 reviewer |
| **Major** | New tier, dependency rule change, principle change | RFC + ADR + 2 reviewers + 10-day review |

### 15.3 Ratification Record

On ratification, append:

```markdown
## Ratification History

| Version | Date | ADR | Summary |
|---------|------|-----|---------|
| 1.0.0 | YYYY-MM-DD | ADR-0000 | Initial ratification |
```

---

## Appendix A — Tier Dependency Diagram

```
                    ┌─────────────┐
                    │  Tier 0     │
                    │  bible/     │  (non-importable law)
                    └─────────────┘
                           │ governs
                           ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Tier 7      │    │  Tier 6      │    │  Tier 4      │
│  prompts/    │    │  workspace/  │    │  service/    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    ┌──────────────┐
                    │  Tier 3      │
                    │  capability/ │
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │  Tier 2      │
                    │  core/       │◄────┐
                    └──────┬───────┘     │
                           ▼             │ implements
                    ┌──────────────┐     │
                    │  Tier 1      │     │
                    │  kernel/     │     │
                    └──────────────┘     │
                                         │
                    ┌──────────────┐     │
                    │  Tier 5      │─────┘
                    │  infra/      │
                    └──────────────┘

        ┌──────────────┐         ┌──────────────┐
        │  Tier E      │         │  Governance  │
        │  experiments/│         │  rfc/ adr/   │
        │  (sandbox)   │         │  logs/       │
        └──────────────┘         └──────────────┘
              ▲
              │ may read production
              │ production may NOT import
```

---

## Appendix B — Change-Class Quick Reference

| Touch | Class | RFC | ADR | Reviewers |
|-------|-------|-----|-----|-----------|
| `bible/` normative text | C0/C3 | Yes | Yes | 1–2 |
| `core/` port breaking | C2 | Yes | Yes | 2 |
| `kernel/` loop behavior | C2 | Yes | Yes | 2 |
| New `capability/` | C2 | Yes | Yes | 1 |
| New `infrastructure/` adapter | C2 | Yes | Yes | 1 |
| `prompts/` stable layer | C2 | Yes | Yes | 1 |
| Internal refactor | C1 | No | No | 1 |
| `experiments/` only | — | No | No | 0 |

---

## Ratification History

| Version | Date | ADR | Summary |
|---------|------|-----|---------|
| 1.0.0 | 2026-06-20 | Pending ADR-0000 | Initial ratification of Volume 00 |

---

*End of Volume 00 — HROS Architecture Constitution*
