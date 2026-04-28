# PHASE2_CONDITION_PLAN

## Scope

First usable Phase 2 Condition backend flow, without breaking Phase 1 behavior.

## API Surface

- `POST /api/patients/{id}/conditions`
- `GET /api/patients/{id}/conditions`
- `GET /api/conditions/{id}`

All responses follow existing facade style:

```json
{
  "ok": true,
  "data": {},
  "source": {}
}
```

Errors keep `ok=false` and `error.code/message/httpStatus`.

## Minimal Create Payload

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

`payload.code` or `payload.codeText` is required.

## Safety / Compatibility

- Phase 1 endpoints (`/api/patients/{id}/intake-summary`, `/api/patients/intake`, `/api/patients/{id}/intake`, `/api/process`) remain unchanged.
- New logic is isolated under `/conditions` routes.
- Error mapping adds `CONDITION_NOT_FOUND` only; no breaking changes to existing codes.

## Verification Checklist

1. Seed patient data (or ensure target patient exists).
2. Call create condition endpoint.
3. List conditions by patient and verify created id appears.
4. Read condition by id and verify payload fields.
5. Confirm Phase 1 intake endpoints still return expected structure.
