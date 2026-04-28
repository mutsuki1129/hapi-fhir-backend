# PHASE2_TASKS

## Goal

Deliver Phase 2 backend additions in small, non-breaking batches on top of the existing Phase 1 facade.

## Guardrails

- Keep existing Phase 1 Patient/Observation flows unchanged.
- Keep facade response envelope stable (`ok/data/error`).
- Add new resources incrementally and independently.
- Avoid schema/contract churn on existing Phase 1 endpoints.

## Phase 2 Work Breakdown

### P0 - Foundation

1. Confirm Phase 2 scope and Phase 1 limitations baseline.
2. Define Phase 2 endpoint docs and validation/repro commands.
3. Extend error mapping for new resource not-found cases.

### P1 - Condition (first delivery)

1. Add `POST /api/patients/{id}/conditions` (create Condition).
2. Add `GET /api/patients/{id}/conditions` (list by patient).
3. Add `GET /api/conditions/{id}` (single read for follow-up fetch).
4. Keep payload minimal and compatible with HAPI R4 Condition core fields.
5. Add reproducible command set for create/read verification.

### P2 - Media / DocumentReference (next)

1. Define upload/reference strategy and metadata contract.
2. Add patient-scoped list/create endpoints.
3. Keep linkage with Patient/Condition lightweight.

### P3 - Practitioner workflow hardening

1. Add Practitioner list/create/edit facade routes.
2. Align Observation/Condition author or asserter references.
3. Add minimal search/filter contract for frontend page usage.

## Implementation Status (this batch)

- [x] Phase 2 Condition create/list/read facade API
- [x] Error mapping extension for Condition not found
- [x] Endpoint documentation and repro steps
- [ ] Media / DocumentReference facade flow
- [ ] Practitioner page workflow
