# Backend Repo Baseline

## Inventory

- README: present at `README.md`; updated for Phase 1 backend scope.
- `.gitignore`: present; covers `.env`, Python cache, logs, local editor files, and local temporary artifacts.
- Docs structure: added `docs/` for backend baseline and hardening support docs.
- Git metadata: this local folder currently does not appear to be a git working tree. `git status` fails with `not a git repository`.

## Files That Should Be Committed

Backend baseline:

- `README.md`
- `.gitignore`
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.auth.yml`
- `config/*.yaml`
- `scripts/*.ps1`
- `scripts/import_ui_server.py`
- `fhir-model/definitions/*.json`
- `fhir-model/examples/*.sample.*`
- `fhir-model/examples/phase1-intake-create.sample.json`
- `fhir-model/questionnaire/*.json`
- `PHASE1_FRONTEND_ENDPOINTS.md`
- `OPERATIONOUTCOME_UI_MAPPING.md`
- `SERVER_CAPABILITY.md`
- `BACKEND_GAPS_FOR_PHASE1.md`
- `docs/*.md`

Canonical shared planning docs currently live outside this workspace:

- `C:\Users\clamp\Desktop\project\fhir document\common\project\PHASE1_RELEASE_NOTES.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\project\PHASE1_KNOWN_LIMITATIONS.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\project\PHASE1_HARDENING.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\project\PHASE2_SCOPE.md`

Repo-local backend/reference docs should be kept aligned with:

- `C:\Users\clamp\Desktop\project\fhir document\common\backend\SERVER_CAPABILITY.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\backend\BACKEND_GAPS_FOR_PHASE1.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\backend\FRONTEND_FHIR_USAGE.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\backend\FRONTEND_PHASE1_PLAN.md`
- `C:\Users\clamp\Desktop\project\fhir document\common\backend\INTEGRATION_TASKS_PHASE1.md`

## Files That Should Stay Local

- `.env`
- `*.log`
- `ui-server.out.log`
- `ui-server.err.log`
- `scripts/__pycache__/`
- `.tmp/`
- `tmp/`
- `hapi-main.war`
- editor state such as `.idea/` and `.vscode/`

## Phase 1 Backend Boundary

In scope:

- HAPI FHIR R4 dev/auth startup.
- Phase 1 facade on `http://127.0.0.1:8092`.
- Patient and Observation workflows already verified for Phase 1.
- CORS at the facade layer.
- OperationOutcome normalization into frontend-friendly error codes.
- Seed data and smoke-test commands for frontend hardening.

Out of scope:

- Formal Condition integration.
- Formal Media or DocumentReference integration.
- Practitioner CRUD or Practitioner page workflows.
- Large facade expansion.
- Broad HAPI architecture refactoring.
