# Development Workflow

PersonaOS should be developed through small, traceable daily updates.

This workflow keeps the codebase, tests, and long-term project documents aligned as the system grows from architecture into implementation.

## Daily Update Process

### 1. Implement Features

Begin with a focused feature or architectural improvement.

Changes should be small enough to understand and review. Prefer extending the existing modular engine structure over introducing broad rewrites. For backend work, preserve the boundaries between Persona, Memory, Knowledge, Skill, Confidence, and Evolution systems.

### 2. Run Tests

Run the relevant test suite after implementation.

At minimum, run tests for the area that changed. When a core engine or shared model changes, run the full test suite.

Record the test command and result in `DAILY_PROGRESS.md`.

### 3. Update `DAILY_PROGRESS.md`

Update `DAILY_PROGRESS.md` during or at the end of each development day.

Use it for daily project continuity:

- What was completed today.
- Which files changed.
- Which tests were run.
- Important design decisions.
- Problems, notes, or blockers.
- Recommended next-session tasks.

This file is the daily development journal. It should be specific to what actually changed.

### 4. Update `CHANGELOG.md`

Update `CHANGELOG.md` when a feature, behavior, milestone, or user-visible project capability is completed.

Use it for project history:

- Completed features.
- New architecture milestones.
- New models or engines.
- Test coverage milestones.
- Design decisions that affect future development.
- Current status and next immediate tasks when a milestone closes.

Do not use the changelog for every tiny edit. Use it when progress is meaningful enough for future developers to understand the project timeline.

### 5. Update `PROJECT_CONTEXT.md`

Update `PROJECT_CONTEXT.md` when the architecture, implementation status, or handoff context changes.

Use it for long-term continuity between developers and AI assistants:

- New core systems or major modules.
- Completed architecture layers.
- Changed responsibilities between engines.
- New implementation status.
- New test status.
- Updated next development direction.

This file should remain accurate to the current repository, not aspirational.

### 6. Update `ROADMAP.md`

Update `ROADMAP.md` when project priorities or phase status changes.

Use it for planning:

- A phase becomes current or complete.
- The immediate project priority changes.
- A major future phase is added, removed, or clarified.
- The order of development changes.

Do not update the roadmap for routine implementation details unless they affect the long-term plan.

### 7. Commit Changes To Git

Commit changes after implementation, tests, and documentation updates are complete.

Commits should be small and focused. A good commit should represent one coherent unit of progress, such as a model addition, an engine capability, a test suite expansion, or a documentation milestone.

When practical, commit implementation changes separately from documentation-only synchronization changes. This keeps code review and project-status updates easier to inspect.

## Document Update Guide

## Documentation Synchronization Policy

PersonaOS completion status depends on documentation synchronization. A bug
fix, feature, or milestone is not considered complete until the required
project documents are updated.

### Bug Fix

Required documentation:

- `CHANGELOG.md`
- `DAILY_PROGRESS.md`
- `HANDOFF.md`

### Feature Completion

Required documentation:

- `CHANGELOG.md`
- `DAILY_PROGRESS.md`
- `HANDOFF.md`
- `PROJECT_CONTEXT.md`

### Milestone Completion

Required documentation:

- `CHANGELOG.md`
- `DAILY_PROGRESS.md`
- `HANDOFF.md`
- `PROJECT_CONTEXT.md`
- `ROADMAP.md`

No milestone may be marked complete in conversation, handoff notes, roadmap
status, or release summaries until the required documentation is synchronized.

### `DAILY_PROGRESS.md`

Update every development day.

Use for daily notes, test results, files changed, and next-session guidance.

### `CHANGELOG.md`

Update when completed work should be part of the project history.

Use for milestones, completed features, and important design decisions.

### `PROJECT_CONTEXT.md`

Update when future developers or AI assistants need a new understanding of the current system.

Use for architecture changes, implementation status changes, and handoff accuracy.

### `ROADMAP.md`

Update when priorities or phase status changes.

Use for planning, not daily implementation detail.

### `docs/*.md`

Update architecture documents when the design changes or when a new subsystem needs conceptual definition.

Architecture docs should explain intent, responsibilities, boundaries, and future direction. They should not contain implementation code.

## Recommended End-Of-Day Checklist

Before ending a development session:

- Confirm code changes are focused.
- Run relevant tests.
- Run the relevant manual smoke test when a runtime path, provider path, or CLI path changes.
- Verify the current automated test number before recording it.
- Apply the Documentation Synchronization Policy for bug fixes, feature completions, and milestone completions.
- Record test results in `DAILY_PROGRESS.md`.
- Update `CHANGELOG.md`, `HANDOFF.md`, `PROJECT_CONTEXT.md`, and `ROADMAP.md` according to the required synchronization level.
- Verify current and next phases match across project documents.
- Review `git status`.
- Inspect untracked files before committing.
- Use `git clean -n` only as a preview when checking removable untracked files.
- Never run `git clean -f` without checking the preview first.
- Commit the completed work.
- Push when the committed work is ready to share.
- Confirm the working tree is clean after the push.

The goal is to keep PersonaOS understandable across sessions. Each day should leave the next developer or AI assistant with a clear map of what changed, what passed, what matters, and what comes next.
