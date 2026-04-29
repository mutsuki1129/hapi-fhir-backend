# Phase X Verification (X1 + X3)

更新日期：2026-04-29  
驗證埠：`http://127.0.0.1:8093`

## 1) X1 驗證摘要

- `/.well-known/smart-configuration`：PASS
- Patient/Observation GET scope enforcement：PASS（401/403）
- `200` 基線：PASS（`mode=dev`）

## 2) X1 證據（保留）

1. `GET /.well-known/smart-configuration` -> `200`
2. `GET /api/patients/patient-001/intake-summary?mode=auth`（無 token） -> `401`
3. 同路徑 + `X-SMART-Scopes: patient/Patient.read` -> `403`
4. 同路徑 `mode=dev` -> `200`

## 3) X3 新增驗證（Condition read + linkage）

### A. Condition read 401

```http
GET /api/patients/patient-001/conditions?mode=auth
```

結果：`401`，`error.code=UNAUTHORIZED`

### B. Condition read 403

```http
GET /api/patients/patient-001/conditions?mode=auth
Authorization: Bearer test-token
X-SMART-Scopes: patient/Patient.read
```

結果：`403`，`error.code=FORBIDDEN`，含 `requiredScopes`

### C. Condition read 200（可重現）

```http
GET /api/patients/patient-001/conditions?mode=auth&baseUrl=http://localhost:8091
Authorization: Bearer test-token
X-SMART-Scopes: patient/Condition.read
```

結果：`200`，`ok=true`，回應含 `source.linkage.model=patient-latest`

### D. Linkage 欄位（intake summary）

```http
GET /api/patients/patient-001/intake-summary?mode=dev
```

結果：`200`，`source.linkage` 可見 `explicit` / `explicit_or_fallback` 訊號。

## 4) 結論

X3 第一階段完成：
1. 已提供可判斷關聯策略的最小回應欄位（linkage）
2. Condition read scope enforcement 已落地且可重現 `401/403/200`
