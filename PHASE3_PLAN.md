# PHASE3_PLAN

## 目標
1. 維持 Phase 1/2 契約穩定。
2. 完成 Phase 3 契約文件硬化與封版前檢查基線。

## 里程碑進度

### M1（完成）
- [x] `docs/phase3-field-dictionary.md`

### M2（完成）
- [x] `docs/phase3-error-contract.md`

### M3（完成）
- [x] `docs/phase3-resource-linkage-contract.md`
- [x] `docs/phase3-facade-response-fields.md`

### M4（完成）
- [x] `docs/phase3-practitioner-contract.md`

### M5（本輪完成）
- [x] `docs/phase3-m5-smoke-checklist.md`
- [x] 封版前契約收斂檢查項文件化（field dictionary / error / practitioner 對照）
- [x] 更新待辦與文件索引同步

## 風險（仍在）
1. Conflict 錯誤尚未逐端點全面落地。
2. Practitioner identifier 驗證仍為寬鬆策略（相容優先）。
3. patient-level/latest 推論非強一致交易快照。

## 驗收標準
1. M1-M5 文件可直接對照目前 facade 行為。
2. 封版前可依 M5 checklist 執行 smoke。
3. 文件已同步到 `fhir document/backend` 並可由 `DOCUMENT_INDEX.md` 查找。
