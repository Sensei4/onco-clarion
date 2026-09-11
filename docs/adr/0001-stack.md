# ADR 0001: Technology Stack

- Status: accepted
- Date: 2026-09-11
- Context: solo developer, 1–2 year horizon, open source, medical domain

## Decision

Use the following stack:

- **Backend:** Python 3.14 + Django 5 + Django REST Framework
- **Database:** PostgreSQL 16
- **Auth:** Django session-based authentication
- **Frontend:** React 18 + TypeScript + Vite + shadcn/ui + TanStack Query
- **Infra:** Docker Compose in dev; Caddy + Docker Compose on a VPS in prod
- **License:** Apache 2.0

## Rationale

### Why Django, not FastAPI

The project needs authentication, an ORM, migrations, an admin panel,
permissions, and i18n from day one. Django provides all of these out
of the box. FastAPI is faster and more modern, but would require
assembling the same components manually, costing weeks. For a solo
developer with a long horizon, Django's "batteries included" nature
is decisive.

The developer already has production experience with Python/Django,
which removes the learning curve risk.

### Why PostgreSQL, not SQLite or MySQL

- JSONB for flexible fields (contacts, future metadata).
- Full-text search for patient lookup.
- Strong reliability and extension ecosystem.
- Standard in healthcare.

### Why session auth, not JWT (yet)

Django's built-in session auth is sufficient for a server-rendered
SPA behind a login. It is simpler and safer than JWT stored in
localStorage (XSS risk). JWT will be introduced only when needed
(mobile clients, third-party integrations), via
`djangorestframework-simplejwt`.

### Why React + Vite, not Next.js

The application is an internal tool behind a login. SSR and SEO are
not requirements. Vite is faster and simpler for a pure SPA. A
public landing page, if needed later, can be built separately.

### Why shadcn/ui

Not a dependency but a set of copy-pasted components. The developer
owns the code, is not tied to a library version, and gets
professional-looking UI without a dedicated designer.

### Why TanStack Query

Server state management (loading, caching, invalidation) is the
bulk of SPA complexity. TanStack Query removes it, avoiding manual
`useEffect` per request.

### Why Docker Compose, not Kubernetes

One developer. One server. Compose is sufficient for years. Kubernetes
is premature operational complexity.

## Alternatives considered

| Stack                    | Why rejected                                                                      |
| ------------------------ | --------------------------------------------------------------------------------- |
| Node.js + NestJS + React | Fewer batteries included; no admin panel; weaker ORM ecosystem for medical domain |
| Java + Spring Boot       | Verbose; slower solo development                                                  |
| C# + .NET                | Fewer open-source examples in medical domain                                      |
| Python + FastAPI         | Manual assembly of Django's built-ins                                             |
| Go + React               | Immature ORM; slower domain modeling                                              |
| Ruby on Rails            | Smaller healthcare community                                                      |

## Consequences

- Development speed is prioritized over bleeding-edge technology.
- The stack is boring and well-documented — a deliberate choice for
  a multi-year solo project.
- Migration to a different stack later would be costly; this ADR
  should be revisited only if a concrete blocker appears.
