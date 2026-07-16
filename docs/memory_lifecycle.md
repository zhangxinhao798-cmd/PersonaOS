# Memory Lifecycle

The Memory Lifecycle defines how memories move through PersonaOS over time.

It expands the Memory Engine architecture by describing future memory states, operations, and governance expectations. This is an architecture document, not implementation code.

## Why Memory Lifecycle Is Needed

Memory gives continuity to a digital mind, but unmanaged memory can become noisy, outdated, contradictory, or unsafe.

PersonaOS should not treat every stored memory as permanently active or equally reliable. A memory may begin as a fresh observation, become useful active context, later be consolidated into a broader pattern, weaken as confidence or relevance declines, and eventually be forgotten or excluded from normal retrieval.

A lifecycle is needed so the Memory Engine can:

- Preserve meaningful experience without accumulating uncontrolled state.
- Distinguish fresh memories from durable memories.
- Track when memories become outdated, superseded, or unreliable.
- Support consolidation of repeated patterns.
- Provide mechanisms for correction, weakening, and forgetting.
- Preserve traceability when memories influence persona behavior or evolution.

Memory lifecycle management should make long-term continuity healthier, not heavier.

## Memory States

### Newly Created

A newly created memory is a recent memory candidate or record.

It may come from an interaction, event, observation, user statement, system decision, or skill outcome. Newly created memories should preserve source, timestamp, category, confidence, and importance. At this stage, the system should be careful about treating the memory as durable truth.

### Active

An active memory is available for normal retrieval.

Active memories are considered useful enough to influence context assembly when relevant. They may represent stable preferences, recent task context, important events, or recurring patterns. Active status does not mean the memory is unquestionable; confidence and importance should still guide how strongly it is used.

### Consolidated

A consolidated memory represents a higher-level synthesis of related memories.

Consolidation may combine repeated episodic memories into semantic memory, summarize a recurring preference, or compress several related observations into a clearer durable record. Consolidated memories should preserve links to supporting memories or provenance where possible.

### Weakened

A weakened memory remains known to the system but has reduced influence.

A memory may become weakened because it is outdated, contradicted, low-confidence, less important, superseded, or repeatedly not useful. Weakened memories may still be available for audit, conflict resolution, or special retrieval, but they should not dominate active context.

### Forgotten

A forgotten memory is removed from normal retrieval.

Forgetting may mean deletion, expiration, suppression, archival, or exclusion depending on future storage and governance rules. A forgotten memory should not influence ordinary reasoning. In some cases, minimal metadata may be retained for audit or rollback, but the memory itself should no longer act as active context.

## Memory Operations

### Create

Create turns an interaction, event, observation, or decision into a memory record or memory candidate.

Creation should capture content, category, confidence, importance, source, timestamp, and any relevant provenance. Not every interaction should create memory. Creation should favor future usefulness and avoid treating raw conversation history as durable memory.

In the current implementation, conversation-derived creation begins with a
reviewable `MemoryCandidate`, not a `MemoryRecord`. The v1 candidate path is:

```text
Conversation
    -> CandidateExtractor
    -> MemoryCandidate
    -> ReviewQueue
    -> Human Approval
    -> future MemoryEngine promotion
```

`CandidateExtractor` uses deterministic rules only. `ReviewQueue` can approve
or reject candidates, but approval does not automatically create durable memory.
Promotion into `MemoryEngine` is handled by `MemoryPromotionBoundary`.
Approval remains separate from promotion: a candidate must first be approved,
then explicitly passed through the promotion boundary before it becomes a
`MemoryRecord`.

### Retrieve

Retrieve selects memories relevant to the current context.

Retrieval should eventually consider category, source, recency, confidence, importance, persona scope, and task relevance. Retrieved memories should be bounded and packaged so they support reasoning without overwhelming the active context.

### Update

Update revises a memory when new information changes its accuracy, confidence, importance, state, or usefulness.

Updates may strengthen a memory, weaken it, correct it, mark it as superseded, or attach new provenance. Important updates should be traceable so future behavior can explain why a memory changed.

### Consolidate

Consolidate combines related memories into clearer long-term structures.

For example, repeated memories about a user's preferred writing style may support a semantic memory about that preference. Consolidation should reduce clutter while preserving meaningful provenance and avoiding unsupported generalization.

### Forget

Forget removes, suppresses, expires, or archives memory.

Forgetting may happen because a memory is outdated, contradicted, user-requested for removal, privacy-sensitive, superseded, low-value, or outside retention rules. Forgetting is an intentional part of memory health.

## Confidence And Importance

Confidence and importance should influence memory lifecycle decisions separately.

Confidence describes how reliable the memory appears to be. High-confidence memories may come from explicit confirmation, repeated evidence, or trusted system state. Low-confidence memories may come from inference, ambiguity, weak evidence, or outdated context.

Importance describes how much the memory should matter if relevant. High-importance memories may involve strong user preferences, major decisions, safety constraints, project commitments, or durable relationship context. Low-importance memories may be useful but should not dominate retrieval.

Lifecycle examples:

- High confidence and high importance: likely to remain active and be retrieved often when relevant.
- High confidence and low importance: reliable but should have limited influence.
- Low confidence and high importance: should be handled carefully, possibly requiring confirmation.
- Low confidence and low importance: likely candidate for weakening, expiration, or forgetting.

Consolidation should require enough confidence and repeated support. Forgetting should consider both low importance and declining confidence, while still respecting explicit user requests and governance rules.

## Engine Interactions

### Persona Engine

The Persona Engine uses memory to preserve continuity across interactions.

The Memory Engine should provide relevant memories without silently redefining persona identity. If memory suggests a durable change to persona behavior, that change should be surfaced through the Evolution Engine rather than applied implicitly.

### Knowledge Engine

The Knowledge Engine can validate, contradict, or contextualize memories.

Knowledge may help determine whether a memory is outdated, source-backed, superseded, or in conflict with external references. Memory should remain distinct from knowledge: memory preserves experience, while knowledge preserves referenceable information.

### Confidence Engine

The Confidence Engine evaluates how reliable a memory is for the current task.

Confidence signals may influence whether a memory remains active, becomes weakened, requires confirmation, or should be excluded from retrieval. The Confidence Engine can also help detect conflict, uncertainty, or overreliance on weak memories.

### Evolution Engine

The Evolution Engine governs durable changes that arise from memory patterns.

Repeated memories may suggest stable preferences, behavioral changes, or persona evolution. These changes should not happen automatically. The Evolution Engine should evaluate proposals, preserve traceability, and prevent personality drift.

## Future Implementation Direction

The current Memory Engine implementation is intentionally simple. It stores `MemoryRecord` objects in memory and supports basic retrieval filtering.

Future implementation should add lifecycle support incrementally:

- Add an explicit memory state field.
- Add update operations for confidence, importance, category, source, and state.
- Add retrieval filters for lifecycle state and timestamp.
- Add ranking by confidence, importance, recency, and relevance.
- Add persistent storage.
- Add consolidation rules for repeated or related memories.
- Add forgetting rules for expiration, user removal, low relevance, or supersession.
- Add audit metadata for memory changes.
- Add tests for each lifecycle operation.

The long-term goal is a memory system that can grow with a digital mind while remaining curated, inspectable, and safe to revise.
