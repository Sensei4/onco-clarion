# ADR 0002: Domain Model — Queues as Statuses, Events as MTI

- Status: accepted
- Date: 2026-09-11
- Context: modeling oncology patient flow for OncoClarion

## Decision

Three modeling decisions define the core of OncoClarion:

1. **Queues are views over status, not separate tables.**
2. **All time-bound activities are Event subtypes via multi-table
   inheritance (MTI), not a single table with JSON fields.**
3. **CancerCase is a separate entity from Patient.**

## Rationale

### 1. Queues as status filters

In real oncology practice, "waiting list" and "observation list" are
not places where patients are stored — they are _states_ a patient
is in. Modeling them as tables would require copying patient data
between tables on every transition, which is error-prone and breaks
referential integrity.

Modeling them as status filters means:

- A transition is a single row in `StatusTransition` plus an update
  to `CancerCase.status`.
- Every transition is auditable by construction.
- Reports ("how many patients moved from waiting list to treatment
  this month") are simple queries.

### 2. Events as MTI, not a single table with JSON

Two alternatives were considered:

- **Single `Event` table with a JSONB `data` column.**
  Pros: flexible, few tables. Cons: no database-level typing,
  harder validation, JSON queries are less readable, refactoring
  later is painful.
- **One table per event type, linked one-to-one to a base `Event`.**
  Pros: strict typing at the DB level, clean ORM, validation in
  the schema. Cons: more tables, joins.

The project chose MTI because the domain is well understood from
the start (the author has direct oncology experience), so the
flexibility of JSON is not needed. Strict typing pays off over a
1–2 year horizon.

### 3. CancerCase separate from Patient

A patient may have multiple primary tumors over a lifetime
(e.g. breast cancer, then years later a different primary tumor).
Also, one case has its own lifecycle: diagnostics, tumor board,
treatment, remission, possible relapse.

Merging case data into Patient would make both the model and the
UI wrong: the schedule, waiting list, and observation list all
operate on _cases_, not on _people_.

One case = one primary tumor with its metastases. This rule is
written into the domain model and must be respected in all future
features.

## Consequences

- The lifecycle of a case is first-class and observable.
- The Event hierarchy is explicit and typed.
- Some queries require joins across `Event` and its subtypes;
  acceptable at MVP scale.
- Adding a new event type later means adding a new table — cheap,
  and it forces conscious modeling.
