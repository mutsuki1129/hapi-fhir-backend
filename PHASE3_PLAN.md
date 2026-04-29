# PHASE3_PLAN

## 目標
1. 維持既有契約穩定，不破壞 endpoint。
2. 完成 Phase 3 契約文件、回歸驗收、封版收斂與最終驗證。

## 里程碑

### M1（完成）
- [x] `docs/phase3-field-dictionary.md`

### M2（完成）
- [x] `docs/phase3-error-contract.md`

### M3（完成）
- [x] `docs/phase3-resource-linkage-contract.md`
- [x] `docs/phase3-facade-response-fields.md`

### M4（完成）
- [x] `docs/phase3-practitioner-contract.md`

### M5（完成）
- [x] `docs/phase3-m5-smoke-checklist.md`

### M6（完成）
- [x] 契約一致性檢查（field/error/practitioner/linkage）

### M7（完成）
- [x] 封版收斂文件與待辦更新

### M8（完成）
- [x] 確認 `http://127.0.0.1:8092` 可連線
- [x] 重跑 smoke 並取得 `200/400/404/401` 可重現證據
- [x] 更新最終文件 `docs/phase3-release-readiness.md`

## 封版狀態

- 文件收斂：完成
- 回歸驗收：完成（`403` 未覆蓋，列為環境限制）

## 殘餘風險
1. `403` 權限場景尚缺可重現證據。
2. Conflict 錯誤尚未逐端點全面落地。
3. Practitioner identifier 驗證仍為寬鬆策略。
