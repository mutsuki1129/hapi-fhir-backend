# PHASE2 Frontend Endpoints (Condition MVP)

## Scope

This document defines the first Phase 2 backend facade endpoints for `Condition`.
Existing Phase 1 endpoints and response contracts remain unchanged.

- Facade base URL: `http://127.0.0.1:8092`
- Backing FHIR (dev): `http://localhost:8091/fhir`
- Backing FHIR (auth): `http://localhost:8090/fhir`

## Response Shape

Success:

```json
{
  "ok": true,
  "data": {},
  "source": {}
}
```

Error:

```json
{
  "ok": false,
  "error": {
    "code": "CONDITION_NOT_FOUND",
    "message": "Condition was not found.",
    "httpStatus": 404
  }
}
```

## 1) POST /api/patients/{id}/conditions

Create one `Condition` resource for a patient.

### Request

```http
POST /api/patients/phase1-patient-001/conditions
Content-Type: application/json
```

```json
{
  "mode": "dev",
  "payload": {
    "codeText": "Hypertension",
    "code": {
      "system": "http://snomed.info/sct",
      "code": "38341003",
      "display": "Hypertensive disorder, systemic arterial (disorder)"
    },
    "clinicalStatus": "active",
    "verificationStatus": "confirmed",
    "categoryCode": "problem-list-item",
    "categoryText": "Problem List Item",
    "onsetDateTime": "2026-04-28T09:10:00+08:00",
    "note": "Phase 2 minimum condition sample"
  }
}
```

### Success

- HTTP `201`
- `data.condition` contains the created FHIR Condition
- `data.patientId` echoes path patient id

## 2) GET /api/patients/{id}/conditions

List Condition resources for one patient.

### Request

```http
GET /api/patients/phase1-patient-001/conditions?mode=dev
```

### Success

- HTTP `200`
- `data.conditions[]`
- `data.summary.conditionCount`

## 3) GET /api/conditions/{id}

Read one Condition by id.

### Request

```http
GET /api/conditions/{conditionId}?mode=dev
```

### Success

- HTTP `200`
- `data` is the raw FHIR Condition resource

## Notes

- `mode` supports `dev` and `auth`.
- Optional `baseUrl` query/body override is supported for local testing.
- Existing Phase 1 Patient/Observation APIs are not modified by these routes.
