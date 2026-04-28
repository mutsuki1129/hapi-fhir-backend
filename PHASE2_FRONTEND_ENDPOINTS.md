# PHASE2 Frontend Endpoints

## Scope

本文件描述 Phase 2 後端 facade 的新增能力，且不破壞既有 Phase 1 契約。

- Facade base URL：`http://127.0.0.1:8092`
- Dev FHIR base URL：`http://localhost:8091/fhir`
- Auth FHIR base URL：`http://localhost:8090/fhir`

## Common Response

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
    "message": "Submitted data is invalid.",
    "httpStatus": 400
  }
}
```

## Condition（已完成）

- `POST /api/patients/{id}/conditions`
- `GET /api/patients/{id}/conditions`
- `GET /api/conditions/{id}`

建立 payload（最小）：

- `payload.clinicalStatus` 必填（允許值：`active|recurrence|relapse|inactive|remission|resolved`）
- `payload.codeText` 或 `payload.code` 至少一個
- 若有 `payload.code`，則 `payload.code.system`、`payload.code.code` 必填
- 可選：`payload.asserterPractitionerId`（驗證存在後寫入 `Condition.asserter`）

## Media（Phase 2 新增）

- `POST /api/patients/{id}/media`
- `GET /api/patients/{id}/media`

建立 payload（最小）：

- `payload.contentType` 必填
- `payload.url` 必填
- 可選：`title`、`creation`、`note`、`operatorPractitionerId`

## DocumentReference（Phase 2 新增）

- `POST /api/patients/{id}/documents`
- `GET /api/patients/{id}/documents`

建立 payload（最小）：

- `payload.contentType` 必填
- `payload.url` 必填
- 可選：`description`、`title`、`date`

## Practitioner（Phase 2 新增）

- `GET /api/practitioners`
- `POST /api/practitioners`
- `PATCH /api/practitioners/{id}`

查詢支援：

- `name`（query，選填）

建立 payload（最小）：

- `payload.family` 或 `payload.given` 至少一個
- 可選：`active`、`identifierSystem`、`identifierValue`

更新 payload：

- 支援更新 `family`、`given`、`active`、`identifierSystem`、`identifierValue`

## Compatibility Notes

- 既有 Phase 1 endpoint 不變：
  - `GET /api/patients/{id}/intake-summary`
  - `POST /api/patients/intake`
  - `PATCH /api/patients/{id}/intake`
  - `DELETE /api/patients/{id}/intake`
  - `POST /api/process`
- 新增 endpoint 全部沿用 `ok/data/error` 風格，並支援 `mode` 與 `baseUrl`。
