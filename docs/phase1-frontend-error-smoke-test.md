# Phase 1 Frontend Error and Smoke-Test Matrix

## Facade Base

- Default facade URL: `http://127.0.0.1:8092`
- Dev HAPI base behind facade: `http://localhost:8091`
- Auth HAPI base behind facade: `http://localhost:8090`

Start facade:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
```

## Stable Error Envelope

All Phase 1 facade errors should use:

```json
{
  "ok": false,
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "Patient was not found.",
    "httpStatus": 404,
    "fhirIssueCode": "processing",
    "diagnostics": "HAPI-2001: Resource Patient/not-exists is not known",
    "rawOperationOutcome": {}
  }
}
```

Frontend should branch on `error.code`, display `error.message`, and keep `diagnostics` for logs.

## Error Codes

| Scenario | Code | Expected HTTP |
| --- | --- | --- |
| Missing/expired auth | `UNAUTHORIZED` | 401 |
| Insufficient permission | `FORBIDDEN` | 403 |
| Missing Patient | `PATIENT_NOT_FOUND` | 404 |
| Missing Observation | `OBSERVATION_NOT_FOUND` | 404 |
| Other missing FHIR resource | `RESOURCE_NOT_FOUND` | 404 |
| Invalid payload/profile issue | `VALIDATION_ERROR` | 400 |
| Bad request outside validation mapping | `BAD_REQUEST` | 400 |
| HAPI/server failure | `SERVER_ERROR` | 500+ |
| HAPI is unreachable | `NETWORK_ERROR` | 503 |
| HAPI call times out | `TIMEOUT` | 504 |
| Unmapped FHIR failure | `UNKNOWN_ERROR` | source status |

## Smoke-Test Data

Seed Phase 1 data:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed-phase1-test-data.ps1 -Mode dev
```

Expected seed patient:

- Patient id: `phase1-patient-001`
- Practitioner id used as read-only related context: `phase1-practitioner-001`
- Observation count after seed/update: expected to be non-zero; README hardening command expects 9 observations.

## Smoke-Test Requests

Health:

```powershell
curl http://127.0.0.1:8092/health
```

Happy path:

```powershell
curl "http://127.0.0.1:8092/api/patients/phase1-patient-001/intake-summary?mode=dev"
```

Patient not found:

```powershell
curl "http://127.0.0.1:8092/api/patients/not-exists-xyz/intake-summary?mode=dev"
```

Network failure simulation:

```powershell
curl "http://127.0.0.1:8092/api/patients/phase1-patient-001/intake-summary?baseUrl=http://127.0.0.1:65535"
```

Expected network response:

```json
{
  "ok": false,
  "error": {
    "code": "NETWORK_ERROR",
    "httpStatus": 503
  }
}
```

## Boundary Notes

This file supports frontend hardening for Patient and Observation flows only. It does not define Condition, Media, DocumentReference, or Practitioner workflow contracts.
