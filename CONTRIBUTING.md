# Contributing to OncoClarion

Thanks for your interest. This project is in early development and
the contribution process will evolve. The rules below are the
minimum.

## Who we are looking for

- **Clinicians** (oncologists, medical informaticians) — to review
  the domain model and workflows.
- **Developers** — Python/Django, React/TypeScript, DevOps.
- **Translators** — once the localization framework is in place.

## Before you start

For anything larger than a typo fix, please open an issue first
and describe what you plan to do. This avoids wasted work.

## Development setup

> Requires Docker Desktop.

    git clone https://github.com/Sensei4/onco-clarion.git
    cd onco-clarion
    cp .env.example .env
    docker compose up

Detailed instructions will be added in Phase 0.

## Code style

- Backend: PEP 8, enforced by Ruff. Type hints where practical.
- Frontend: ESLint + Prettier. TypeScript strict mode.
- Commits: Conventional Commits
  (https://www.conventionalcommits.org/).
- Branches: `feat/...`, `fix/...`, `docs/...`, `chore/...`.

## Pull requests

- One logical change per PR.
- Reference the related issue.
- Add tests where practical.
- Update documentation if behavior changes.

## License

By contributing, you agree that your contributions are licensed
under the Apache License 2.0.
