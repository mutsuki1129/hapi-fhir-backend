# Phase X X1 Verification

更新日期：2026-04-29  
驗證埠：`http://127.0.0.1:8093`

## 1) 驗證摘要

- `/.well-known/smart-configuration`：PASS
- Patient/Observation GET scope enforcement：PASS（401/403 可重現）
- `200` 基線：PASS（`mode=dev`）
- `mode=auth` + 測試 token：受上游 token 驗證限制，回 `401`（已知限制）

## 2) 證據

1. SMART 設定端點  
   - Request: `GET /.well-known/smart-configuration`  
   - Result: `200`，回傳 issuer/scopes/capabilities

2. 無 token（auth）  
   - Request: `GET /api/patients/patient-001/intake-summary?mode=auth`  
   - Result: `401`，`error.code=UNAUTHORIZED`

3. scope 不足（auth）  
   - Header: `Authorization: Bearer test-token` + `X-SMART-Scopes: patient/Patient.read`  
   - Result: `403`，`error.code=FORBIDDEN`

4. dev 成功基線  
   - Request: `GET /api/patients/patient-001/intake-summary?mode=dev`  
   - Result: `200`，`ok=true`

5. auth scope 通過但 token 無效  
   - Header: `Authorization: Bearer test-token` + `X-SMART-Scopes: patient/*.read`  
   - Result: 上游 `401`（預期限制）

## 3) 結論

X1 最小 SMART 落地完成：
1. smart configuration endpoint 已可用
2. Patient/Observation GET 已有最小 scope enforcement（401/403）
3. 可重現腳本與限制已文件化
