# Phase 2 Condition Contract

本文件定義 Phase 2 Condition MVP 的 facade 契約、欄位規則與錯誤碼，供前後端協作使用。

## Endpoint

- `POST /api/patients/{id}/conditions`
- `GET /api/patients/{id}/conditions`
- `GET /api/conditions/{id}`

Base URL（預設）：`http://127.0.0.1:8092`

## 回應格式

成功：

```json
{
  "ok": true,
  "data": {},
  "source": {}
}
```

失敗：

```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Condition payload validation failed.",
    "httpStatus": 400,
    "details": []
  }
}
```

## Create Payload 規則（最小但明確）

`POST /api/patients/{id}/conditions` 的 request body：

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

驗證規則：

1. `payload.clinicalStatus` 必填，且必須為：
   - `active`
   - `recurrence`
   - `relapse`
   - `inactive`
   - `remission`
   - `resolved`
2. `payload.codeText` 或 `payload.code` 至少要有一個。
3. 若提供 `payload.code`，則 `payload.code.system` 與 `payload.code.code` 皆為必填。

## patient 專屬查詢規則

`GET /api/patients/{id}/conditions` 透過 FHIR 條件查詢：

`GET {baseUrl}/fhir/Condition?subject=Patient/{id}&_count=200`

此路徑為 patient 範圍查詢，不做全量掃描。

## 錯誤碼

- `VALIDATION_ERROR`：Condition payload 不合規
- `PATIENT_NOT_FOUND`：目標 Patient 不存在
- `CONDITION_NOT_FOUND`：目標 Condition 不存在
- `RESOURCE_NOT_FOUND`：其他資源不存在
- `NETWORK_ERROR` / `TIMEOUT` / `SERVER_ERROR`：上游連線或服務問題

## 範例

### 合規建立

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\",\"code\":{\"system\":\"http://snomed.info/sct\",\"code\":\"38341003\"},\"clinicalStatus\":\"active\"}}"
```

### 不合規建立（缺 clinicalStatus）

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\"}}"
```

預期：`ok=false` 且 `error.code=VALIDATION_ERROR`
