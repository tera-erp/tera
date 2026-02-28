# Tera

YAML-driven, module-based workflow/ERP platform. The backend (FastAPI + PostgreSQL) loads module definitions from YAML; the frontend (React + Vite + Tailwind) renders screens dynamically.

## For Devs

### Modules

- `module`: metadata (`id`, `name`, `version`, `description`, `icon`, `color`).
- `screens`: list/detail/form/dashboard/custom; endpoints, permissions, layout/widgets/actions.
- `forms`: fields, validation, visibility rules, computed formulas, layout hints, nested arrays.
- `workflows`: states, transitions, guards, permissions.
- `actions`: `api`/`custom`/`batch` with endpoints and success/error handling.
- `permissions`: strings contributed by the module.
- `menu`: optional navigation tree.

- Backend: `app/main.py` boots; `modules.initialize_modules()` loads YAML into memory. APIs in `app/routers/modules.py` expose modules/screens/workflows. Action/workflow logic in `app/modules/core/*`.
- Frontend: `ui/src/pages/ModuleScreenPage.tsx` drives module routes. Renderers live in `ui/src/modules/components`; engines/types in `ui/src/modules/*` handle actions/workflows.


### Getting started

- Prereqs: Python 3.10+ with Poetry; Node.js (LTS) + npm; PostgreSQL.
- Backend: `poetry install && poetry run uvicorn tera.main:app --reload`
- Frontend: `npm install --prefix ui && npm run dev --prefix ui`
- Database: set env vars used by `app/core/config.py`; run `poetry run alembic upgrade head` (or `python run_migrations.py`).

### Adding a module (today)

External modules are not fully supported without implementing nasty workarounds.

1. Scaffold `app/modules/<your_module>/` with a `configs/` folder. Use `app/modules/finance/configs/*.yaml` or `app/modules/payroll/configs/*.yaml` as a template (base, domain screens, workflows, menu). Keep YAML schemas aligned with `app/modules/core/module.py`.
2. (Optional) Add `router.py`/`models.py` under your module if you need new endpoints or persistence; otherwise reuse existing routers. Ensure every `screens.*.endpoint` and `actions.*.endpoint` you declare has a FastAPI handler.
3. Restart the backend so `initialize_modules()` reloads configs.
4. Frontend will render list/detail/form screens from the fetched config. Only register custom React components via `ModuleFactory` when you need bespoke UI beyond the generic renderers.

### Extensibility

- Planned support for custom extension modules: pluggable React components and server hooks so users can ship UI/logic without forking core.
