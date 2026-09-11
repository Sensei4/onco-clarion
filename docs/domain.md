# Domain Model

This document describes the core domain of OncoClarion. It is the
single source of truth for data modeling decisions. Any change to
the model must be reflected here and, if significant, in a new ADR.

## Guiding principles

1. **Patient ≠ Case.** A patient is a person. A cancer case is one
   primary tumor with its metastases. One patient may have several
   cases over a lifetime.
2. **Queues are views, not tables.** "Waiting list" and "observation
   list" are not entities. They are filtered queries over cases in a
   given status.
3. **Everything that happens is an Event.** Visits, tumor boards,
   hospitalizations, and treatments are all Events with different
   types and type-specific details.
4. **Every status change is logged.** The lifecycle of a case is
   auditable.
5. **Regulatory neutrality.** The model does not assume a specific
   jurisdiction. Localization and compliance are deployment concerns.

## Entities

### Organization

A clinic, dispensary, or hospital.

| Field      | Type     | Notes              |
| ---------- | -------- | ------------------ |
| id         | UUID     |                    |
| name       | string   |                    |
| country    | string   | ISO 3166-1 alpha-2 |
| created_at | datetime |                    |

### User

Custom user model from day one. Extends `AbstractUser`.

| Field        | Type              | Notes                                |
| ------------ | ----------------- | ------------------------------------ |
| id           | UUID              |                                      |
| organization | FK → Organization |                                      |
| full_name    | string            |                                      |
| role         | enum              | `doctor`, `admin` (extensible later) |
| email        | string            | login identifier                     |
| is_active    | bool              |                                      |

Roles are intentionally minimal in MVP. The enum is extensible
without schema migration.

### Patient

| Field                 | Type              | Notes                                |
| --------------------- | ----------------- | ------------------------------------ |
| id                    | UUID              |                                      |
| organization          | FK → Organization |                                      |
| full_name             | string            |                                      |
| birth_date            | date              |                                      |
| sex                   | enum              | `male`, `female`, `other`, `unknown` |
| medical_record_number | string            | unique per organization              |
| contacts              | jsonb             | phone, address, etc.                 |
| vital_status          | enum              | `alive`, `dead`                      |
| created_at            | datetime          |                                      |

`vital_status` lives on the patient, not on the case. A person dies
once; cases are separate.

### CancerCase

One primary tumor with its metastases.

| Field             | Type              | Notes                                          |
| ----------------- | ----------------- | ---------------------------------------------- |
| id                | UUID              |                                                |
| patient           | FK → Patient      |                                                |
| organization      | FK → Organization |                                                |
| diagnosis_code    | string            | ICD-O-3 morphology + ICD-10 topography         |
| diagnosis_text    | string            | free text                                      |
| verification_date | date              | date of morphological verification             |
| tnm_t             | string            | T0–T4, TX                                      |
| tnm_n             | string            | N0–N3, NX                                      |
| tnm_m             | string            | M0, M1, MX                                     |
| stage             | string            | I–IV (derived from TNM, editable by clinician) |
| status            | enum              | see lifecycle below                            |
| created_at        | datetime          |                                                |

#### CancerCase lifecycle

    new → diagnostic → consilium → waiting_hospitalization
        → in_treatment → observation → remission
                                     ↘ relapse → consilium
                                     ↘ terminal

`relapse` returns the case to the `consilium` stage — this is what
makes the model cyclical, matching real oncology practice.

### Event (base table)

Single base entity for everything that happens in time.

| Field        | Type              | Notes                             |
| ------------ | ----------------- | --------------------------------- |
| id           | UUID              |                                   |
| case         | FK → CancerCase   |                                   |
| patient      | FK → Patient      | denormalized for fast queries     |
| organization | FK → Organization |                                   |
| type         | enum              | see subtypes below                |
| scheduled_at | datetime          | when planned                      |
| occurred_at  | datetime          | when actually happened (nullable) |
| status       | enum              | `planned`, `done`, `cancelled`    |
| author       | FK → User         | who created/performed             |
| notes        | text              |                                   |

#### Event subtypes (multi-table inheritance)

- `EventPrimaryVisit` — first visit
- `EventFollowupVisit` — follow-up visit
- `EventConsilium` — tumor board (recorded after the fact)
- `EventHospitalization` — admission
- `EventTreatment` — treatment course (chemo, radiation, surgery)
- `EventObservationVisit` — planned visit during observation

Each subtype is a separate table with a one-to-one link to `Event`.
Type-specific fields live there, not in JSON. This gives us strict
typing at the database level.

### Referral

A request for a diagnostic procedure (lab, histology, cytology,
imaging). Has its own lifecycle — it can be ordered, completed, or
cancelled independently of the Event that created it.

| Field              | Type            | Notes                                              |
| ------------------ | --------------- | -------------------------------------------------- |
| id                 | UUID            |                                                    |
| case               | FK → CancerCase |                                                    |
| event              | FK → Event      | the visit that issued the referral                 |
| type               | enum            | `lab`, `histology`, `cytology`, `imaging`, `other` |
| status             | enum            | `ordered`, `completed`, `cancelled`                |
| ordered_at         | datetime        |                                                    |
| result_text        | text            | free text in MVP                                   |
| result_received_at | datetime        |                                                    |

### Document

| Field       | Type            | Notes                                     |
| ----------- | --------------- | ----------------------------------------- |
| id          | UUID            |                                           |
| case        | FK → CancerCase |                                           |
| event       | FK → Event      | nullable                                  |
| type        | enum            | `conclusion`, `scan`, `analysis`, `other` |
| file_path   | string          | path in object storage                    |
| uploaded_by | FK → User       |                                           |
| uploaded_at | datetime        |                                           |

Files are stored in filesystem/object storage, not in the database.
The database holds only metadata and the path.

### StatusTransition

Audit trail of case lifecycle changes. This is what makes the
patient flow observable and reportable.

| Field           | Type            | Notes    |
| --------------- | --------------- | -------- |
| id              | UUID            |          |
| case            | FK → CancerCase |          |
| from_status     | string          |          |
| to_status       | string          |          |
| transitioned_by | FK → User       |          |
| transitioned_at | datetime        |          |
| reason          | text            | nullable |

### AuditEvent

Security audit — who viewed or changed what.

| Field       | Type      | Notes                                 |
| ----------- | --------- | ------------------------------------- |
| id          | UUID      |                                       |
| user        | FK → User |                                       |
| action      | enum      | `view`, `create`, `update`, `delete`  |
| entity_type | string    | e.g. `Patient`, `CancerCase`, `Event` |
| entity_id   | UUID      |                                       |
| timestamp   | datetime  |                                       |
| ip_address  | string    |                                       |

`StatusTransition` and `AuditEvent` serve different purposes:
the former is business logic, the latter is security. Both are
required.

## Queues

Queues are **queries**, not tables.

| Queue            | Query                                                                |
| ---------------- | -------------------------------------------------------------------- |
| Schedule         | Events of visit types with `status=planned`, `scheduled_at` in range |
| Waiting list     | `CancerCase` with `status=waiting_hospitalization`                   |
| Observation list | `CancerCase` with `status=observation`                               |
| Remission        | `CancerCase` with `status=remission`                                 |
| Deceased         | `Patient` with `vital_status=dead`                                   |

## What is intentionally NOT in MVP

- Reports and analytics
- Cross-organization data exchange
- DICOM viewer
- Mobile app
- FHIR export
- Localization beyond English UI scaffolding
- Hospitalization module with wards and beds
- Automatic status transitions
- Roles beyond `doctor` and `admin`

## English-only UI (for now)

All UI strings are in English. Backend uses Django's i18n framework
(`gettext_lazy`) from day one so that translation can be added later
without refactoring. Medical terminology follows international
standards (TNM, ICD-O-3).
