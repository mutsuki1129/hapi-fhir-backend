# Phase X Scope Enforcement (X1)

## 1) 範圍

X1 先在 Patient/Observation 讀取路徑加最小 enforcement：
- `GET /api/patients/{id}/intake-summary?mode=auth`

## 2) 行為規則

1. 無 Bearer token：回 `401 UNAUTHORIZED`
2. scope 不足：回 `403 FORBIDDEN`
3. scope 通過：
   - 若上游 auth FHIR token 有效，回 `200`
   - 若上游 token 無效/缺失，回上游 `401`

## 3) Scope 判定

啟用開關：
- `SMART_SCOPE_ENFORCEMENT`（預設啟用）

測試 header（X1 最小驗證用）：
- `X-SMART-Scopes`（預設允許，可由 `SMART_ALLOW_SCOPE_HEADER` 關閉）

通過條件：
- `patient/*.read`，或
- 同時具備 `patient/Patient.read` + `patient/Observation.read`

## 4) 可重現驗證（X1）

### 401（無 token）

```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/intake-summary?mode=auth"
```

### 403（scope 不足）

```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/intake-summary?mode=auth" `
  -H "Authorization: Bearer test-token" `
  -H "X-SMART-Scopes: patient/Patient.read"
```

### 200（dev 基線可重現）

```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/intake-summary?mode=dev"
```

## 5) 備註

在無可用真實 auth token 的本地環境，`mode=auth` 的 scope 通過後仍可能回上游 `401`，此為預期限制，已由 X1 驗證文件記錄。
