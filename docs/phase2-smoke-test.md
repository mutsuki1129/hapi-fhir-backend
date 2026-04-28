# Phase 2 Smoke Test (Backend)

## Prerequisites

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
powershell -ExecutionPolicy Bypass -File .\scripts\seed-phase1-test-data.ps1 -Mode dev
```

## 1) Condition

建立：

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\",\"code\":{\"system\":\"http://snomed.info/sct\",\"code\":\"38341003\"},\"clinicalStatus\":\"active\"}}"
```

查詢：

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions?mode=dev"
```

## 2) Media

建立：

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/media" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"contentType\":\"image/jpeg\",\"url\":\"https://example.org/media/phase2-xray.jpg\",\"title\":\"X-ray sample\"}}"
```

查詢：

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/patients/phase1-patient-001/media?mode=dev"
```

## 3) DocumentReference

建立：

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/documents" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"contentType\":\"application/pdf\",\"url\":\"https://example.org/docs/phase2-report.pdf\",\"description\":\"Phase2 report\"}}"
```

查詢：

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/patients/phase1-patient-001/documents?mode=dev"
```

## 4) Practitioner

建立：

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/practitioners" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"family\":\"Chen\",\"given\":\"Wei\",\"identifierSystem\":\"urn:clinic:doctor-id\",\"identifierValue\":\"phase2-practitioner-001\"}}"
```

查詢：

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/practitioners?mode=dev&name=Chen"
```

## 5) Practitioner 更新

```powershell
curl.exe -sS -X PATCH "http://127.0.0.1:8092/api/practitioners/{practitionerId}" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"given\":\"Wei-Lun\"}}"
```

## 6) Validation Error Check

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Missing clinicalStatus\"}}"
```

預期：`ok=false` 且 `error.code=VALIDATION_ERROR`
