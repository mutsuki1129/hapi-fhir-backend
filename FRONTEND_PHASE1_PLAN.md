# FRONTEND Phase 1 Plan (Patient + Observation)

## Goal
Refactor frontend data flow to integrate with backend FHIR contracts for:
- `Patient`
- `Observation` (temperature only)

Do not perform large UI redesign in phase 1.

## Non-Goals (Phase 1)
- Full replacement of all legacy routes.
- Doctor module (`Practitioner`) full redesign.
- Condition/image clinical workflow (`kondisi`, `picture`) final model.

## 1) Target UX Scope

## 1.1 Keep and adapt now
- Patients list/create/edit pages.
- Medical records list/create/edit pages, but only temperature observation workflow.

## 1.2 Defer or freeze
- Doctor CRUD pages (until Practitioner API contract is finalized).
- `kondisi` and prescription image persistence as clinical truth.

## 2) Frontend Data Contract Strategy

Add a frontend adapter layer so UI does not depend on old DB fields.

### 2.1 View models used by pages

```ts
// Patient list/form
interface PatientVM {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  photoUrl?: string;
}

// Temperature record list/form
interface TemperatureObservationVM {
  id: string;
  patientId: string;
  patientDisplay?: string;
  performerId?: string; // optional in phase 1 if Practitioner unavailable
  performerDisplay?: string;
  valueCelsius: number;
  effectiveDateTime?: string;
  note?: string; // temporary landing for old kondisi if needed
}
```

### 2.2 FHIR mapping functions
- `fromFhirPatient(resource: Patient): PatientVM`
- `toFhirPatient(vm: PatientVM): Patient`
- `fromFhirObservation(resource: Observation): TemperatureObservationVM`
- `toFhirObservation(vm: TemperatureObservationVM): Observation`

## 3) API Integration Plan (Backend-first)

Use backend-provided FHIR endpoints (exact URL to align with backend team).

## 3.1 Patient
- List: `GET Patient`
- Read: `GET Patient/{id}`
- Create: `POST Patient`
- Update: `PUT/PATCH Patient/{id}`

## 3.2 Observation (temperature)
- List by patient: `GET Observation?subject=Patient/{id}&code=8310-5`
- List global (if needed): `GET Observation?code=8310-5`
- Read: `GET Observation/{id}`
- Create: `POST Observation`
- Update: `PUT/PATCH Observation/{id}`

Observation payload in phase 1 should enforce:
- `code` = body temperature (LOINC `8310-5`)
- `valueQuantity.system` = `http://unitsofmeasure.org`
- `valueQuantity.code` = `Cel`

## 4) Page-by-Page Refactor Tasks

## 4.1 Patients pages
- Keep UI layout.
- Replace data source from `Pasien` local model to `PatientVM` from FHIR adapter.
- Remove/disable fields not in phase 1 Patient contract:
  - `age`, `height`, `weight`, `role_id`, `password` (for clinical patient forms).
- Keep search/sort in UI layer only for fields available from FHIR response.

## 4.2 Medical records pages
- Keep card/table UI.
- Replace source from local `rekams` join to `TemperatureObservationVM`.
- Create/edit form should submit only phase 1 observation fields:
  - patient reference
  - performer reference (optional if Practitioner not ready)
  - valueCelsius
  - effectiveDateTime
- Treat old `kondisi` and `picture` as temporary UI-only/deferred fields:
  - Option A: hide in phase 1
  - Option B: show as read-only and mark as "legacy"

## 4.3 Group-by views
- Rebuild grouping using Observation VM keys:
  - by `patientId`
  - by `performerId`
- Do not depend on SQL alias fields (`name_pasien`, `name_dokter`).

## 5) Compatibility Layer During Transition

To avoid breaking existing screens while backend evolves:
- Add a feature flag, for example `FHIR_PHASE1_ENABLED`.
- If enabled, pages consume FHIR adapters.
- If disabled, fallback to legacy controllers temporarily.

This enables incremental rollout without large UI rewrite.

## 6) Validation and Error Handling

- Centralize FHIR validation error translation to existing alert components.
- Normalize backend OperationOutcome to UI error format.
- Keep current top-level success/error alert UX.

## 7) Testing Plan

## 7.1 Update E2E scripts for phase 1
- Add patient create/edit/list checks via new data contract.
- Add temperature observation create/edit/list/group checks.
- Remove assumptions about legacy fields (`kondisi`, `picture`) in phase 1 happy path.

## 7.2 Acceptance criteria
- No page in phase 1 depends on local tables `pasiens/dokters/rekams` for primary data flow.
- Patient pages work end-to-end via Patient resource.
- Medical record pages work end-to-end for temperature Observation.
- Existing UI layout remains mostly unchanged.

## 8) Implementation Sequence

1. Add adapter and API client modules (no UI changes).
2. Migrate Patients list/create/edit to adapter.
3. Migrate Medical Records list/create/edit (temperature only).
4. Migrate grouped record views to adapter grouping.
5. Update e2e scripts and run regression.
6. Freeze legacy-only fields and document phase 2 scope.

## 9) Phase 2 Preview (Out of scope now)
- `Condition` integration for clinical condition text.
- `Media` or `DocumentReference` integration for image evidence.
- Practitioner-first redesign for doctor module.