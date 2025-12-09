# Tera

YAML-driven, module-based Workflow platform. Backend (FastAPI + PostgreSQL) loads module definitions from YAML and exposes them via APIs; the frontend (React + Vite + Tailwind) 

## Architecture

- **Data flow**: Author Modules + YAML configs -> backend loads -> frontend fetches via `/api/v1/modules` -> UI renders per screen type -> actions/workflows call declared endpoints.

- **Module configs**: Each business module lives in `app/modules/<module>/config.yaml`. The schema is defined in `app/modules/core/module.py` (Pydantic models for module, screens, forms, workflows, actions, permissions, menu).

- **Backend runtime**:
  - `modules.initialize_modules()` (called in `app/main.py`) loads/validates YAML into an in-memory registry.
  - API surface in `app/routers/modules.py`: list modules, get a module, and fetch screens/workflows/permissions.
  - Actions and workflows enforced server-side via `app/modules/core/action.py` and `WorkflowState` in `module.py`.

- **Frontend runtime (UI factory)**:
  - Routes like `/modules/:moduleId/:screenId(/:recordId)` handled by `ui/src/pages/ModuleScreenPage.tsx`.
  - Renderers in `ui/src/modules/components` build list/detail/form screens from YAML data.
  - `ActionHandler` and `WorkflowEngine` in `ui/src/modules` execute client actions and guard workflow transitions.


## Module YAML (high level)

- `module`: metadata (`id`, `name`, `version`, `description`, `icon`, `color`).
- `screens`: list/detail/form/dashboard/custom screens; each declares endpoints, permissions, and renderer config (columns, widgets, layout, actions).
- `forms`: field schemas with validation, visibility rules, computed formulas, layout hints, and nested arrays.
- `workflows`: state machine (`initial_state`, states, transitions with permissions and guards).
- `actions`: `api`/`custom`/`batch` actions with endpoints, success/error messages, and post-success behaviors.
- `permissions`: flat list the module contributes.
- `menu`: optional navigation tree for module landing pages.

## Repository layout

- Backend: `app/` (FastAPI entry: `app/main.py`), database config in `app/core/database.py`, routers in `app/routers/*`, modules in `app/modules/*`.
- Frontend: `ui/` (Vite + React + Tailwind), dynamic module rendering in `ui/src/modules/*`, pages in `ui/src/pages/*`.
- Migrations: `alembic/` (run via `run_migrations.py` or Alembic CLI).
- CI: `.github/workflows/sast-scan.yml` runs CodeQL on push/PR to main/develop and nightly; findings auto-issue when alerts exist.

## Local development

### Prerequisites

- Python 3.10+, Poetry
- Node.js + npm
- PostgreSQL running locally

### Backend

```bash
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend

```bash
npm install --prefix ui
npm run dev --prefix ui
```

### Database

- Configure env vars (or `.env`) consumed by `app/core/config.py` (DB URL, JWT secret, etc.).

## Adding a new module

tbd. at the moment only internal modules are supported `app/modules/**`

- Frontend will render list/detail/form screens dynamically.
- We plan to support custom extension modules (pluggable React components and server hooks) so partners can ship bespoke UI/logic without forking core.
