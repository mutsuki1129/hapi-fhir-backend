# PHASE1 Frontend Endpoints

## Scope

Phase 1 exposes a small backend facade for frontend integration while the canonical FHIR server remains HAPI FHIR R4.

- Default facade base URL: `http://127.0.0.1:8092`
- Dev FHIR base URL behind facade: `http://localhost:8091/fhir`
- Auth FHIR base URL behind facade: `http://localhost:8090/fhir`
- Phase 1 clinical resources: `Patient` and `Observation`
- Deferred to later phases: `Condition`, `Media` / `DocumentReference`, Practitioner pages and final Practitioner workflow

Start the facade:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
```

Health check:

```http
GET /health
```

Success response:

```json
{
  "status": "UP",
  "service": "phase1-backend"
}
```

## Common Request Options

For facade endpoints that call HAPI, requests can pass:

| Field | Location | Default | Notes |
| --- | --- | --- | --- |
| `mode` | query/body | `dev` | Allowed values: `dev`, `auth` |
| `baseUrl` | query/body | derived from `mode` | Use only for local override/testing |

## Common Response Shape

Success:

```json
{
  "ok": true,
  "data": {}
}
```

Error:

```json
{
  "ok": false,
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "Patient was not found.",
    "httpStatus": 404,
    "fhirIssueCode": "processing",
    "diagnostics": "HAPI-2001: Resource Patient/not-exists-xyz is not known",
    "rawOperationOutcome": {}
  }
}
```

See `OPERATIONOUTCOME_UI_MAPPING.md` for the code mapping.

## 1. GET /api/patients/{id}/intake-summary

Returns a Phase 1 summary for one patient. The facade reads:

- `Patient/{id}`
- `Observation?subject=Patient/{id}&_count=200`
- `CareTeam?subject=Patient/{id}&_count=50`
- referenced `Practitioner` resources when present

Practitioner and CareTeam are included only as related read-only context for the existing intake summary. This endpoint does not implement Practitioner CRUD or Practitioner page workflows.

### Request

```http
GET /api/patients/phase1-patient-001/intake-summary?mode=dev
```

### Success Response

```json
{
  "ok": true,
  "data": {
    "patient": {
      "resourceType": "Patient",
      "id": "phase1-patient-001"
    },
    "observations": [],
    "careTeams": [],
    "practitioners": [],
    "summary": {
      "patientId": "phase1-patient-001",
      "observationCount": 9,
      "careTeamCount": 1,
      "practitionerCount": 1
    }
  },
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Patient", "Observation", "CareTeam", "Practitioner"]
  }
}
```

### Error Response

```json
{
  "ok": false,
  "error": {
    "code": "PATIENT_NOT_FOUND",
    "message": "Patient was not found.",
    "httpStatus": 404
  }
}
```

## 2. POST /api/patients/intake

Creates the existing intake bundle through `scripts/create-patient-intake.ps1`, then returns the intake summary when a patient id is available.

### Request Body

```json
{
  "mode": "dev",
  "payload": {
    "patient": {
      "id": "phase1-patient-002",
      "family": "Chang",
      "given": "YuHan",
      "gender": "female",
      "birthDate": "1994-03-16",
      "nationalId": "G223456789",
      "nhiCardNo": "NHI99881122"
    },
    "doctor": {
      "id": "phase1-practitioner-001",
      "family": "Lin",
      "given": "JiaMin"
    },
    "intake": {
      "educationLevel": "Bachelor",
      "occupation": "Data Analyst",
      "monthlyIncome": 85000,
      "monthlyExpense": 47000,
      "hobby": "Yoga, books, travel",
      "psychologicalTraits": "Calm, curious, self-disciplined",
      "behaviorPattern": "Regular routine and moderate exercise"
    },
    "biomarker": {
      "code": "4548-4",
      "display": "Hemoglobin A1c/Hemoglobin.total in Blood",
      "value": 5.8,
      "unit": "%"
    },
    "extraAttributes": {
      "incomeSource": "Salary",
      "livingStatus": "Lives with family"
    }
  }
}
```

### Success Response

- `ok` is `true`
- `data.summary.patientId` contains the created patient id when summary collection succeeds
- `logs` contains script output for diagnostics

## 3. PATCH /api/patients/{id}/intake

Updates the existing intake fields through `scripts/update-patient-intake.ps1`, then returns the updated intake summary.

### Request Body

```json
{
  "mode": "dev",
  "payload": {
    "monthlyIncome": 92000,
    "hobby": "Running, photography",
    "behaviorPattern": "Regular exercise and fixed sleep schedule"
  }
}
```

### Supported Payload Keys

- `nameFamily`
- `nameGiven`
- `gender`
- `birthDate`
- `newNationalId`
- `nhiCardNo`
- `educationLevel`
- `occupation`
- `monthlyIncome`
- `monthlyExpense`
- `hobby`
- `psychologicalTraits`
- `behaviorPattern`
- `biomarkerCode`
- `biomarkerDisplay`
- `biomarkerValue`
- `biomarkerUnit`
- `doctorPractitionerId`
- `doctorFamily`
- `doctorGiven`

### Success Response

- `ok` is `true`
- `data` contains the refreshed intake summary
- `logs` contains script output for diagnostics

## 4. CSV Import UI Compatibility Endpoint

The existing CSV upload UI still uses:

```http
POST /api/process
```

This endpoint accepts `csvText`, `mode`, optional `baseUrl`, `validateOnly`, and `continueOnValidationError`.

## 5. CORS

The facade sends these headers:

- `Access-Control-Allow-Origin`: value from `-CorsOrigin`, default `*`
- `Access-Control-Allow-Methods`: `GET,POST,PATCH,OPTIONS`
- `Access-Control-Allow-Headers`: `Content-Type, Authorization`

Use a specific origin for staging/production instead of `*`.

## 6. Phase 1 Hardening Checklist

- Facade endpoints expose a stable `ok/data/error` response shape.
- HAPI `OperationOutcome` is mapped to UI-readable error codes.
- CORS is explicit at the facade layer.
- Patient not found is normalized as `PATIENT_NOT_FOUND`.
- Validation and script failures are normalized as `VALIDATION_ERROR` / `BAD_REQUEST` where possible.
- `Condition`, `Media`, `DocumentReference`, and Practitioner workflow implementation remain out of scope.

