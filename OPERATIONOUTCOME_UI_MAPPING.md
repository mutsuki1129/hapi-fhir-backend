# OPERATIONOUTCOME UI Mapping (Phase 1)

## Purpose

HAPI FHIR returns errors as FHIR `OperationOutcome`. The Phase 1 facade normalizes those responses into a small UI-friendly error envelope so the frontend can show stable messages without parsing every FHIR issue shape.

## Facade Error Shape

```json
{
  "ok": false,
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "Patient was not found.",
    "httpStatus": 404,
    "fhirIssueCode": "processing",
    "diagnostics": "HAPI-2001: Resource Patient/not-exists-xyz is not known",
    "rawOperationOutcome": {
      "resourceType": "OperationOutcome",
      "issue": []
    }
  }
}
```

## Mapping Rules

| Source condition | UI code | UI message |
| --- | --- | --- |
| HTTP 401 | `UNAUTHORIZED` | Authentication is required. Please sign in again. |
| HTTP 403 | `FORBIDDEN` | You do not have permission to perform this action. |
| HTTP 404 and diagnostics references `Patient/` | `PATIENT_NOT_FOUND` | Patient was not found. |
| HTTP 404 and diagnostics references `Observation/` | `OBSERVATION_NOT_FOUND` | Observation was not found. |
| HTTP 404 and diagnostics references `Condition/` | `CONDITION_NOT_FOUND` | Condition was not found. |
| HTTP 404 and diagnostics references `Media/` | `MEDIA_NOT_FOUND` | Media was not found. |
| HTTP 404 and diagnostics references `DocumentReference/` | `DOCUMENTREFERENCE_NOT_FOUND` | DocumentReference was not found. |
| HTTP 404 and diagnostics references `Practitioner/` | `PRACTITIONER_NOT_FOUND` | Practitioner was not found. |
| HTTP 404 otherwise | `RESOURCE_NOT_FOUND` | Requested resource was not found. |
| HTTP 400 and `issue.code` is `invalid`, `structure`, `value`, or `processing` | `VALIDATION_ERROR` | Submitted data is invalid. Please review the highlighted fields. |
| HTTP 400 otherwise | `BAD_REQUEST` | Request could not be processed. |
| HTTP >= 500 | `SERVER_ERROR` | Server error. Please try again later. |
| Network connection failure | `NETWORK_ERROR` | FHIR server is unreachable. Please check the backend connection. |
| Request timeout | `TIMEOUT` | FHIR request timed out. Please try again. |
| Any other FHIR failure | `UNKNOWN_ERROR` | FHIR operation failed. |

## HAPI-Specific Normalization

HAPI not-found responses commonly include:

```text
HAPI-2001: Resource Patient/not-exists-xyz is not known
```

When diagnostics contain `HAPI-2001` and `not known`, the facade maps:

- `Patient/...` diagnostics to `PATIENT_NOT_FOUND`
- `Observation/...` diagnostics to `OBSERVATION_NOT_FOUND`
- `Condition/...` diagnostics to `CONDITION_NOT_FOUND`
- `Media/...` diagnostics to `MEDIA_NOT_FOUND`
- `DocumentReference/...` diagnostics to `DOCUMENTREFERENCE_NOT_FOUND`
- `Practitioner/...` diagnostics to `PRACTITIONER_NOT_FOUND`
- other resource diagnostics to `RESOURCE_NOT_FOUND`

## Frontend Usage Guidance

1. Prefer `error.code` for UI branching.
2. Display `error.message` to users.
3. Log `diagnostics` for developer troubleshooting when present.
4. Keep `rawOperationOutcome` for debugging only; do not build UI behavior from it.

## Phase 1 / Phase 2 Boundary

This mapping started in Phase 1 and is extended in Phase 2 for `Condition`, `Media`, `DocumentReference`, and `Practitioner` facade workflows. Existing Phase 1 endpoint contracts remain unchanged.
