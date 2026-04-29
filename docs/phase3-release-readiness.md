# Phase 3 Release Readiness (M8 Final)

更新日期：2026-04-29

## 結論

- 最終狀態：**Conditional PASS**
- 判定說明：契約文件與主要 smoke 驗證可重現；`403` 在目前環境未能自然觸發，列為已知驗證缺口。

## 1) 契約一致性檢查（M6）

已對照：
- `docs/phase3-field-dictionary.md`
- `docs/phase3-error-contract.md`
- `docs/phase3-practitioner-contract.md`
- `docs/phase3-resource-linkage-contract.md`

結果：
- `ok/data/error` 包裝一致
- Practitioner list/create/edit 文件與現行 facade 行為一致
- 錯誤碼分類（validation / not-found / unauthorized）可對應

## 2) M5/M6/M7 Smoke 重跑結果（M8）

驗證環境：
- Facade: `http://127.0.0.1:8092`（可連線）
- Dev FHIR: `http://localhost:8091/fhir`（可連線）

證據摘要：

1. `GET /health`  
   - HTTP `200`  
   - 回應：`{"status":"UP","service":"phase1-backend"}`

2. `GET /api/practitioners?mode=dev`  
   - HTTP `200`  
   - 回應：`ok=true`，`data.items[]`、`data.summary.count` 存在

3. `POST /api/practitioners`（validation case：缺 family/given）  
   - HTTP `400`  
   - `error.code=VALIDATION_ERROR`

4. `PATCH /api/practitioners/not-exists-001`  
   - HTTP `404`  
   - `error.code=PRACTITIONER_NOT_FOUND`

5. `POST /api/patients/patient-001/conditions`（validation case：缺 clinicalStatus）  
   - HTTP `400`  
   - `error.code=VALIDATION_ERROR`

6. `POST /api/patients/patient-001/conditions`（valid payload）  
   - HTTP `200/201`（本次成功）  
   - 回應 `ok=true`，已建立 Condition（id: `1265`）

7. `GET /api/practitioners?mode=auth`（無 token）  
   - HTTP `401`  
   - `error.code=UNAUTHORIZED`

8. `403` 驗證  
   - 本環境未提供可穩定重現 `403` 的授權角色/權限場景  
   - 狀態：未覆蓋（deferred）

## 3) M7 封版收斂狀態

已完成：
- Phase 3 契約主文件齊備（field/error/linkage/practitioner/m5-checklist/release-readiness）
- `PHASE3_PLAN.md` 更新至 M8
- `待辦事項/Phase 3/backend-待辦.md` 已更新
- 文件已同步到 `fhir document/backend` 並更新索引

## 4) 殘餘風險與下一步

1. `403` 尚未有可重現證據  
   - 下一步：在具 RBAC/角色限制環境補測並附證據。

2. Conflict 錯誤尚未逐端點全面落地  
   - 下一步：分批盤點可回 `409 CONFLICT_ERROR` 的情境。

3. Practitioner identifier 仍為寬鬆驗證  
   - 下一步：與前端確認後以 deprecation window 推進加嚴。
