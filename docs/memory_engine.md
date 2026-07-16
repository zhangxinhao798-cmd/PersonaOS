# Memory Engine

The Memory Engine is the continuity layer of PersonaOS.

It defines how a digital mind records, retrieves, evaluates, updates, consolidates, and forgets experience-derived information over time. It does not replace conversation history, knowledge storage, persona definition, or language model context. It provides durable memory as a structured system capability.

## Purpose

The purpose of the Memory Engine is to preserve meaningful continuity across interactions.

PersonaOS treats memory as more than a transcript. Memory is selected, structured, weighted, and revisable information that can influence future reasoning. It may include user preferences, prior decisions, recurring patterns, important events, relationship context, unresolved goals, and learned interaction cues.

Memory should help a digital mind behave as though experience matters, while avoiding uncontrolled accumulation of raw conversation residue. It exists to support continuity, personalization, adaptation, and self-consistency without turning every past message into permanent truth.

## What Memory Means

In PersonaOS, memory is experience-derived context that may be useful beyond the moment in which it was created.

A memory should generally include:

- The content or claim being remembered.
- The source or origin of the memory.
- The category of memory it belongs to.
- The importance of the memory.
- The confidence assigned to the memory.
- Relevant timestamps or lifecycle metadata.
- Links to related memories, if available.
- Rules or constraints governing future use.

Memory is not automatically equivalent to fact. A memory may record that a user said something, preferred something, requested something, or that the system inferred something. These distinctions matter. The Memory Engine should preserve provenance so future components can evaluate how strongly a memory should influence behavior.

## Memory And Conversation History

Conversation history is the record of what was said.

Memory is the structured interpretation of what may need to persist.

Conversation history may be long, noisy, temporary, and session-specific. It can contain false starts, jokes, contradictions, outdated instructions, and details that should not become lasting context. Memory is intentionally narrower. It extracts durable signals from interaction history and stores them in a form that can be retrieved, updated, challenged, or forgotten.

The distinction is important because a digital mind should not treat every prior utterance as equally authoritative. A passing comment, a stable preference, a confirmed biographical detail, and a task-specific instruction should not all have the same status.

The Memory Engine may use conversation history as an input, but it should not expose raw history as memory without evaluation.

## Memory Candidate Review Boundary

PersonaOS now defines an explicit candidate layer between runtime conversation
and durable memory.

The intended flow is:

```text
Conversation
    -> CandidateExtractor
    -> MemoryCandidate
    -> ReviewQueue
    -> Human Approval
    -> MemoryEngine
```

`MemoryCandidate` is a reviewable proposal, not a durable memory record.
`CandidateExtractor` is deterministic and rule-based in v1. It can identify
simple user preferences, long-term goals, explicit personal facts, and stable
habits, but it does not call an LLM, summarize conversation, or approve
anything automatically.

`ReviewQueue` stores pending, approved, and rejected candidates in memory.
Approval means the candidate has passed review for a future promotion path; it
does not write to `MemoryEngine` by itself.

`MemoryPromotionBoundary` is the explicit bridge from an approved candidate to
durable memory. It validates that the candidate is approved, maps candidate
content, category, confidence, importance, timestamp, and provenance into a
`MemoryRecord`, then calls `MemoryEngine.create_memory()`. Runtime sessions,
session managers, candidate extractors, and review queues must not call
`MemoryEngine` directly.

This boundary protects the distinction between conversation and memory. Runtime
sessions may produce memory candidates, but conversation turns must never become
durable memory without review.

## Responsibilities

The Memory Engine is responsible for:

- Creating memory records from significant interactions or system events.
- Retrieving relevant memories for the current context.
- Updating memories when new evidence changes their usefulness or accuracy.
- Consolidating related memories into clearer long-term structures.
- Forgetting memories when they expire, lose relevance, are superseded, or must be removed.
- Distinguishing memory categories and retrieval scopes.
- Tracking importance, confidence, provenance, and recency.
- Providing memory context to the Persona Engine without redefining persona identity.
- Supporting inspection, correction, and future governance of memory state.

The Memory Engine should not become the whole state of the system. It stores continuity-bearing experience, while knowledge, persona, confidence, and evolution remain separate architectural concerns.

## Memory Categories

### Working Memory

Working memory contains short-term context needed for the current task, session, or reasoning window.

It may include active goals, recent references, temporary constraints, pending questions, and information needed to complete an in-progress interaction. Working memory is high-relevance but low-durability by default. Most working memory should expire naturally unless promoted into another category.

### Episodic Memory

Episodic memory records meaningful events and interactions.

It may include prior conversations, milestones, user decisions, conflicts, achievements, project history, or moments that explain why a current state exists. Episodic memory preserves experience as situated context: what happened, when it happened, who was involved, and why it mattered.

Episodic memory should support continuity without requiring the system to replay entire conversations.

### Semantic Memory

Semantic memory stores generalized understanding derived from experience.

It may include stable user preferences, recurring patterns, learned concepts, domain assumptions, relationship context, and durable facts about the operating environment. Semantic memory is less tied to a single event than episodic memory. It represents what the system has learned across events.

Semantic memory should be especially careful about confidence and provenance, because repeated exposure does not always mean truth.

### Procedural Memory

Procedural memory is an optional category for learned methods, routines, workflows, and behavioral patterns.

It may include preferred ways to perform recurring tasks, interaction protocols, tool-use habits, or project-specific operating procedures. Procedural memory should remain distinct from persona rules. It can guide behavior, but changes to core identity or long-term operating principles should flow through explicit persona or evolution mechanisms.

## Importance And Confidence

Memory records should carry both importance and confidence.

Importance describes how much a memory should matter if it is relevant. A high-importance memory may represent a strong user preference, a safety constraint, a major decision, or an enduring project fact. A low-importance memory may still be useful, but it should not dominate context selection.

Confidence describes how reliable the memory is. A high-confidence memory may come from explicit confirmation, repeated evidence, or trusted system state. A low-confidence memory may come from inference, ambiguity, weak signals, or outdated context.

Importance and confidence are different. A memory can be important but uncertain, such as an inferred user need that should be handled carefully. A memory can also be reliable but unimportant, such as a minor preference with limited effect.

The Memory Engine should expose these signals so the Persona Engine and Confidence Engine can decide how strongly a memory should influence output.

## Memory Lifecycle

### Create

Creation is the process of turning an interaction, event, observation, or system decision into a memory candidate.

Memory creation should evaluate whether the information is durable, meaningful, permissioned, and useful. Not every interaction deserves memory. Creation should capture provenance and distinguish explicit user statements from system inferences.

### Retrieve

Retrieval is the process of selecting memories relevant to the current interaction or system event.

Retrieval should consider semantic similarity, direct references, recency, importance, confidence, category, permissions, and persona-level constraints. Retrieved memories should be ranked and packaged in a form that helps reasoning without overwhelming the active context.

### Update

Update is the process of revising an existing memory when new evidence appears.

Updates may strengthen confidence, reduce confidence, change importance, add detail, mark a memory as superseded, or correct inaccurate content. The Memory Engine should prefer traceable revision over silent mutation when the change affects future behavior.

### Consolidate

Consolidation is the process of combining related memories into clearer long-term representations.

For example, several episodic memories about repeated user choices may support a semantic memory about a stable preference. Consolidation reduces clutter, resolves duplication, and helps the system preserve patterns without storing every detail forever.

Consolidation should not erase meaningful provenance. Long-term summaries should preserve links to supporting memories when possible.

### Forget

Forgetting is the process of removing, expiring, suppressing, or archiving memory.

Forgetting may occur because a memory is outdated, low-value, contradicted, privacy-sensitive, superseded, user-requested for removal, or no longer useful. Forgetting is not only deletion. In some cases, a memory may be retained for audit or conflict resolution while being excluded from normal retrieval.

PersonaOS should treat forgetting as an intentional part of memory health, not as failure.

## Interaction With Persona Engine

The Persona Engine uses the Memory Engine to retrieve continuity-bearing context before significant reasoning or interaction.

Memory informs persona expression by providing relevant history, preferences, and experience-derived context. It should not silently rewrite persona identity. If a memory suggests a lasting change to behavior, priorities, or self-description, that change should be explicit and may require coordination with the Evolution Engine.

The boundary is:

- Memory preserves what has been experienced or learned.
- Persona defines the active identity and behavioral frame.
- Evolution governs durable changes to that identity or behavior.

The Persona Engine may request memories by task, user, topic, time range, category, or importance threshold. The Memory Engine should return relevant context with enough metadata for responsible use, including confidence and provenance when available.

## High-Level Retrieval Flow

At a high level, memory retrieval follows this flow:

1. Receive a retrieval request from the Persona Engine or another authorized system component.
2. Interpret the current context, including task, user, active persona, and constraints.
3. Identify candidate memories across relevant categories.
4. Rank candidates by relevance, importance, confidence, recency, and permission.
5. Resolve conflicts, duplicates, and outdated entries where possible.
6. Package selected memories with category, confidence, importance, and provenance signals.
7. Return a bounded memory context for use in reasoning or response generation.
8. Record retrieval metadata when useful for later evaluation or debugging.

This flow is conceptual. It describes responsibility and coordination, not a required implementation sequence.

## Design Principles

### Memory Is Curated

The system should remember selectively. Durable memory should be created because it has expected future value, not because it appeared in a transcript.

### Provenance Matters

The system should preserve where a memory came from and how it was derived. Explicit user statements, system observations, and model inferences should remain distinguishable.

### Memory Is Revisable

Memories may become outdated, contradicted, or less useful. The Memory Engine should support correction and refinement without pretending earlier context never existed.

### Retrieval Is Contextual

The right memory depends on the current situation. Memory retrieval should be scoped, ranked, and bounded so it supports reasoning rather than flooding it.

### Forgetting Is Healthy

Long-term continuity requires removal as well as retention. Forgetting supports privacy, relevance, accuracy, and system maintainability.

### Boundaries Are Explicit

Memory should remain separate from persona, knowledge, confidence, and evolution. Clear boundaries make the system easier to inspect, govern, and extend.

## Future Extensibility

The Memory Engine should support future expansion without requiring a redesign of PersonaOS.

Possible areas of extension include:

- User-facing memory inspection and correction tools.
- Memory permissions, privacy policies, and retention controls.
- Multiple memory stores for different personas, users, projects, or environments.
- Advanced consolidation strategies for long-term pattern learning.
- Conflict detection between memories with different confidence levels.
- Retrieval evaluation and feedback loops.
- Memory versioning, audit trails, and rollback support.
- Integration with vector stores, graph stores, relational stores, or hybrid memory systems.
- Shared memory boundaries for collaboration between digital minds.
- Explicit promotion paths from working memory to episodic, semantic, or procedural memory.

The long-term goal is not to make PersonaOS remember everything. It is to give digital minds a durable, inspectable, and responsible way to carry meaningful experience forward.
