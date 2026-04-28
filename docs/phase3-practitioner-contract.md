# Phase 3 Practitioner Contract (M4)

本文件定義 Practitioner facade 在 Phase 3 M4 的最小穩定契約（list/create/edit）。
目標是對齊請求欄位、回應欄位與錯誤碼，且不破壞既有 endpoint。

## 1) Endpoint 範圍（不變更）

- `GET /api/practitioners`
- `POST /api/practitioners`
- `PATCH /api/practitioners/{id}`

共用查詢/請求控制欄位：
- `mode`: `dev` | `auth`（預設 `dev`）
- `baseUrl`: 可選，僅測試覆蓋用

## 2) List 契約

### Request
- Method: `GET`
- Path: `/api/practitioners`
- Query:
  - `name`（可選）：姓名關鍵字
  - `mode`（可選）
  - `baseUrl`（可選）

### Success Response

```json
{
  "ok": true,
  "data": {
    "items": [],
    "summary": {
      "count": 0
    }
  },
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Practitioner"]
  }
}
```

`items[]` 為 FHIR Practitioner resource 原樣回傳（不做破壞性重塑）。

### Error Response（對齊 phase3-error-contract）
- `VALIDATION_ERROR`（400）
- `BAD_REQUEST`（400）
- `NETWORK_ERROR`（503）
- `TIMEOUT`（504）
- `SERVER_ERROR`（5xx）
- `UNKNOWN_ERROR`（其他未分類）

## 3) Create 契約

### Request
- Method: `POST`
- Path: `/api/practitioners`
- Body:

```json
{
  "mode": "dev",
  "payload": {
    "family": "Lin",
    "given": "Doctor",
    "active": true,
    "identifierSystem": "urn:clinic:doctor-id",
    "identifierValue": "DR0001"
  }
}
```

### 欄位規則（M4 凍結）
- `payload` 必須是 object。
- `payload.family` 或 `payload.given` 至少一個必填。
- `identifierSystem` 與 `identifierValue` 需成對提供（現況未成對時視為可忽略，不報錯）。

### Success Response

```json
{
  "ok": true,
  "data": {
    "practitioner": {}
  },
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Practitioner"]
  }
}
```

### Error Response
- `VALIDATION_ERROR`：`payload.family` 與 `payload.given` 同時缺失等
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`
- `UNKNOWN_ERROR`

## 4) Edit 契約

### Request
- Method: `PATCH`
- Path: `/api/practitioners/{id}`
- Body:

```json
{
  "mode": "dev",
  "payload": {
    "family": "Wang",
    "given": "Mei",
    "active": true,
    "identifierSystem": "urn:clinic:doctor-id",
    "identifierValue": "DR0002"
  }
}
```

### 行為說明
- 先讀取 `Practitioner/{id}`，成功後以 `PUT` 更新。
- 僅更新 payload 有提供的欄位；未提供欄位保持原值。

### Success Response

```json
{
  "ok": true,
  "data": {
    "practitioner": {}
  },
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Practitioner"]
  }
}
```

### Error Response（對齊 phase3-error-contract）
- `PRACTITIONER_NOT_FOUND`（404）
- `VALIDATION_ERROR`（400）
- `BAD_REQUEST`（400）
- `NETWORK_ERROR`（503）
- `TIMEOUT`（504）
- `SERVER_ERROR`（5xx）
- `UNKNOWN_ERROR`

## 5) M4 穩定性結論

1. Practitioner list/create/edit 路徑維持不變，可與既有前端相容。
2. 錯誤碼分類已可對齊 Phase 3 error contract 的 not-found/validation 主分支。
3. 本輪不做破壞性欄位重命名、不新增版本分支。
