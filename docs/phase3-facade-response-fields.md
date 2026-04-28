# Phase 3 Facade Response Fields Note

本文件補充 facade API 的回應欄位說明，不改動既有 endpoint。

## 1) 共用成功回應

```json
{
  "ok": true,
  "data": {},
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Condition"]
  }
}
```

- `ok`: `true` 表示請求成功。
- `data`: 端點主要資料。
- `source.mode`: `dev` 或 `auth`。
- `source.baseUrl`: 實際呼叫 FHIR base URL。
- `source.resourceType`: 本次操作涉及資源型別。

## 2) 共用錯誤回應

```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Submitted data is invalid. Please review the request.",
    "httpStatus": 400,
    "fhirIssueCode": "processing",
    "diagnostics": "payload.code.system is required when payload.code is provided."
  }
}
```

- `error.code`: 前端流程分支主鍵（穩定）。
- `error.message`: 使用者顯示文案（可調整，不建議做分支）。
- `error.httpStatus`: 映射後 HTTP 狀態。
- `error.fhirIssueCode`: FHIR issue code（可選）。
- `error.diagnostics`: 後端/上游錯誤細節（可選，除錯用）。

## 3) 端點 data 最小欄位（Phase 3 現況）

- `GET /api/patients/{id}/conditions`
  - `data.patientId`
  - `data.conditions[]`
  - `data.summary.conditionCount`

- `GET /api/patients/{id}/media`
  - `data.patientId`
  - `data.items[]`
  - `data.summary.mediaCount`

- `GET /api/patients/{id}/documents`
  - `data.patientId`
  - `data.items[]`
  - `data.summary.documentReferenceCount`

- `GET /api/practitioners`
  - `data.items[]`
  - `data.summary.count`
