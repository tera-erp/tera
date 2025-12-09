# Module System + UI Factory Guide

This document captures the current architecture and runtime flow for the YAML-driven module system and the UI Factory layer that renders modules dynamically. It supersedes earlier docs in `docs/`.

## Goals
- Ship new business modules (finance, payroll, inventory, etc.) without shipping new frontend builds.
- Keep a single YAML source of truth per module for screens, forms, workflows, permissions, and menus.
- Make the UI renderers and action/workflow engines generic so they can operate on any valid module config.

## Backend architecture (FastAPI)
- **Config source**: Each module lives under `app/modules/<module_id>/config.yaml` (see `app/modules/finance/config.yaml`, `app/modules/payroll/config.yaml`). The schema is defined by `app/modules/core/module.py` (Pydantic models such as `ModuleConfig`, `ScreenConfig`, `FormConfig`, `WorkflowConfig`, `ActionConfig`).
- **Loader**: `ModuleLoader.load_all(modules_dir)` walks the modules directory (skips `core`, hidden, and non-directories), validates YAML into `ModuleConfig`, and keeps a map keyed by `module.id`.
- **Startup**: `app/main.py` calls `modules.initialize_modules()` once. This populates the in-memory registry `_module_configs` used by the router.
- **API surface** (`app/routers/modules.py`):
  - `GET /api/v1/modules` → list all module configs (sorted by name).
  - `GET /api/v1/modules/{module_id}` → single module config.
  - `GET /api/v1/modules/{module_id}/screens|workflows|permissions` → section-level accessors.
- **Workflow runtime (server)**: `WorkflowState` class in `module.py` encapsulates state machine checks (transition, edit/delete permission), intended for server-side validation.
- **Action runtime (server)**: `app/modules/core/action.py` defines `ActionRegistry` and `execute_action` for custom/server actions. YAML `actions` section references handlers via `<module_id>.<action_name>`.

### YAML schema (high level)
Key sections in a module `config.yaml` (examples: finance, payroll):
- `module`: metadata (`id`, `name`, `version`, `description`, `author`, `icon`, `color`).
- `screens`: map of screen definitions. Supported `type`: `list`, `detail`, `form`, `dashboard`, `custom`.
  - For lists: `endpoint`, `permissions`, `list_config` (columns, search, sort, filters, pagination, row actions).
  - For details: `endpoint`, `detail_config` (form key, sidebar widgets, related records, actions list).
  - For forms: `endpoint`, `permissions`, and optional layout metadata.
- `forms`: map of form configs. Each field declares `type`, `label`, validation, visibility rules (`hidden_if`, `disabled_if`), layout hints, formulas for computed values, and nested `array` field definitions.
- `workflows`: named workflows with `initial_state`, `states` (label/color/can_transition_to/allow_edit/allow_delete), and `transitions` (from/to/label/action/permissions/confirm/disabled_if).
- `actions`: declarative action set. Types: `api`, `custom`, `batch`. For `api`, specify `method`, `endpoint`, `success_message`, `error_message`, `on_success` (e.g., `refresh_form`, `navigate_to`).
- `permissions`: flat list of permission strings contributed by the module.
- `menu`: optional navigation tree for module landing page.

## Frontend architecture (UI Factory layer)
Source: `ui/src/modules/*` and dynamic pages in `ui/src/pages/ModuleScreenPage.tsx`.

- **Module loading**:
  - `ModuleFactory.loadModules()` (planned) fetches `/api/v1/modules` with bearer token and caches configs in-memory.
  - `ModuleScreenPage` (current entry) fetches a single module config via `/api/v1/modules/:moduleId` when a user visits `/modules/:moduleId/:screenId[/ :recordId]`.
- **Routing**:
  - `App.tsx` wires `/modules/:moduleId/:screenId(/:recordId)` through `ModuleScreenPage` inside an auth-protected shell.
  - `ModuleFactory.generateRoutes()` can generate route objects if/when we switch to fully dynamic routing; today we still use `ModuleScreenPage`.
- **Renderers (UI Factory)** (`ui/src/modules/components`):
  - `ListRenderer`: Renders list screens from `list_config` (columns, search, sort, pagination, row actions, selection). Uses React Query for data fetch in callers.
  - `DetailRenderer`: Shows record detail with optional sidebar widgets/metadata/related records and embeds workflows. Can toggle into edit mode to reuse `FormRenderer` for updates.
  - `FormRenderer`: Builds forms from `FormConfig`; supports tabs/accordion/grid layouts, validation rules, visibility conditions, computed formulas, and basic field types. Array/select option loading is stubbed (TODO for dynamic options and nested arrays UI).
  - `DynamicScreen`: Alternate wrapper that chooses renderer by screen type and wires list/detail/form data fetching plus mutations. Not yet the main entry (ModuleScreenPage performs similar logic).
- **Engines**:
  - `ActionHandler`: Executes YAML-defined `actions` on the client. Implements `api` actions (path params substitution, auth header, success/error handling, optional redirect). `custom`/`batch` are placeholders for future client handlers.
  - `WorkflowEngine`: Client-side state machine for `WorkflowConfig` (current state, allowed transitions, history, edit/delete gates). `DetailRenderer` can display available transitions and current state badge.
- **Types**: `ui/src/modules/types.ts` mirrors the backend Pydantic schema so YAML configs round-trip cleanly to the frontend.

## End-to-end flow
1. **Authoring**: Define `config.yaml` under `app/modules/<id>/` using the schema above.
2. **Startup**: FastAPI loads and validates configs via `ModuleLoader`, registers them in-memory.
3. **API access**: Frontend fetches module config(s) from `/api/v1/modules` or `/api/v1/modules/:moduleId`.
4. **Routing**: React Router sends `/modules/:moduleId/:screenId(/:recordId)` to `ModuleScreenPage` (or future dynamic routes from `ModuleFactory`).
5. **Rendering**: The page chooses the renderer based on `ScreenConfig.type` and, when needed, resolves the associated `FormConfig` and `WorkflowConfig` from the fetched module payload.
6. **User actions**: List/detail views call backend endpoints defined in the screen/action configs; workflow transitions and row actions are executed through `ActionHandler`; `WorkflowEngine` guards allowed transitions on the client side.

## How to add a new module
1. Create a folder `app/modules/<your_module>/` with `config.yaml` following the schema (copy from finance/payroll as a starting point).
2. Place API endpoints referenced by the module under the appropriate router (or add new routers) so `screen.endpoint` and `actions.*.endpoint` resolve.
3. Restart the backend (or reload) so `initialize_modules()` re-reads YAML.
4. On the frontend, no build-time changes are required for basic list/detail/form screens—`ModuleScreenPage` renders from the fetched config. If you need custom React components per screen, register them with `ModuleFactory.registerModule()` and wire `screen.component` to the registered key.

## Extending the UI Factory (next steps/TODOs)
- Load select/array options from `FormFieldConfig.endpoint` and render dynamic nested arrays.
- Unify `ModuleScreenPage` with `DynamicScreen` and switch routing to `ModuleFactory.generateRoutes()` once stable.
- Expand `ActionHandler` to support `custom` and `batch` client handlers and honor `on_success` actions (e.g., `refresh_form`, `navigate_to`).
- Add permission guards using `ModuleFactory.hasPermission` and user roles before rendering screens/actions.
- Add widget components for `detail_config.sidebar.widgets` and render related records list/table.

## Quick references
- Backend schema & loader: `app/modules/core/module.py`, `app/modules/core/action.py`.
- Backend API: `app/routers/modules.py` (initialized in `app/main.py`).
- Example configs: `app/modules/finance/config.yaml`, `app/modules/payroll/config.yaml`.
- Frontend UI Factory: `ui/src/modules/*`, `ui/src/pages/ModuleScreenPage.tsx`.
- Static module catalog (legacy cards): `ui/src/config/modules.ts` (still hardcoded; will be replaced by live `/modules` data).
