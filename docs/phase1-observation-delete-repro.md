# Phase 1 Observation Delete Repro

This repro validates the Phase 1 delete flow for observations only.

## 1) Seed sample data

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed-phase1-test-data.ps1 -Mode dev
```

## 2) Confirm intake summary has observations

```powershell
curl "http://127.0.0.1:8092/api/patients/phase1-patient-001/intake-summary?mode=dev"
```

Expect `data.summary.observationCount` to be greater than `0`.

## 3) Delete observations via facade

```powershell
curl -X DELETE "http://127.0.0.1:8092/api/patients/phase1-patient-001/intake?mode=dev"
```

Expected key fields:

- `ok: true`
- `data.deletedObservationCount` is `>= 0`
- `data.patientDeleted: false`

## 4) Verify patient is still present

```powershell
curl "http://localhost:8091/fhir/Patient/phase1-patient-001"
```

Expected HTTP `200` and a valid `Patient` resource.

## 5) Verify observations are removed

```powershell
curl "http://localhost:8091/fhir/Observation?subject=Patient/phase1-patient-001&_count=200"
```

Expected `entry` count to be `0` or no intake observations for the patient.
