# PHASE3_PLAN

## 目標
1. 維持既有契約穩定，不破壞 endpoint。
2. 完成 Phase 3 文件化、回歸驗收與封版收斂。

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

### M6（完成，含阻塞記錄）
- [x] 契約一致性檢查（field/error/practitioner/linkage）
- [x] 依 M5 checklist 執行可重現驗證並文件化結果（環境連線阻塞）

### M7（完成）
- [x] `docs/phase3-release-readiness.md`
- [x] 更新待辦與文件索引

## 封版狀態

- 文件收斂：完成
- 線上 smoke：待環境可連線後補跑

## 主要風險
1. `127.0.0.1:8092` 不可達，M6 runtime 驗證受阻。
2. Conflict 錯誤尚未逐端點全面落地。
3. Practitioner identifier 驗證目前仍為寬鬆策略。
