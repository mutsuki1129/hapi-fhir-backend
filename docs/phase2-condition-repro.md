# Phase 2 Condition Repro

## 1) Start prerequisites

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
powershell -ExecutionPolicy Bypass -File .\scripts\seed-phase1-test-data.ps1 -Mode dev
```

## 2) Create a condition for patient

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\",\"code\":{\"system\":\"http://snomed.info/sct\",\"code\":\"38341003\",\"display\":\"Hypertensive disorder, systemic arterial (disorder)\"},\"clinicalStatus\":\"active\",\"verificationStatus\":\"confirmed\",\"categoryCode\":\"problem-list-item\",\"categoryText\":\"Problem List Item\",\"onsetDateTime\":\"2026-04-28T09:10:00+08:00\",\"note\":\"Phase 2 minimum condition sample\"}}"
```

Expected:

- `ok=true`
- HTTP `201`
- `data.condition.id` exists

## 3) List conditions by patient

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions?mode=dev"
```

Expected:

- `ok=true`
- `data.summary.conditionCount >= 1`

## 4) Read one condition by id

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/conditions/{conditionId}?mode=dev"
```

Expected:

- `ok=true`
- `data.resourceType` equals `Condition`
