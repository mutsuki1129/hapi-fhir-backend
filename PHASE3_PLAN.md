# PHASE3_PLAN

## 目標
1. 維持 Phase 1/2 契約穩定，完成 Phase 3 文件化交付。
2. 讓前後端可依欄位字典、錯誤契約、關聯契約穩定協作。
3. 以最小改動補齊 M3 後端可交付批次。

## 範圍
- M1：欄位字典凍結
- M2：錯誤契約分類（validation/not-found/conflict/timeout）
- M3：關聯一致性契約與 facade 回應欄位說明

## 非目標
- 不改壞既有 endpoint 路徑
- 不變更 `ok/data/error` 包裝
- 不做破壞相容資料結構調整

## 里程碑

### M1（完成）
- [x] `docs/phase3-field-dictionary.md`
- [x] 欄位變更策略（additive first / deprecation window / version note）

### M2（完成）
- [x] `docs/phase3-error-contract.md`
- [x] 錯誤碼策略文件化並維持 `ok/data/error` 一致

### M3（本輪完成）
- [x] `docs/phase3-resource-linkage-contract.md`
- [x] `docs/phase3-facade-response-fields.md`
- [x] 更新 Phase 3 待辦與文件同步索引

## 風險
1. 現況主要為 patient-level/latest 推論，非 transaction 級強一致快照。
2. HAPI diagnostics 文案差異可能影響細部映射。
3. conflict 類錯誤仍需後續逐端點落地。

## 驗收標準
1. M1/M2/M3 文件可直接對照目前 facade 行為。
2. 關聯欄位與查詢模式有清楚定義與風險標示。
3. 文件已同步到 `fhir document/backend` 並更新 `DOCUMENT_INDEX.md`。
