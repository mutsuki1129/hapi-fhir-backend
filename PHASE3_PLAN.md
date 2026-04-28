# PHASE3_PLAN

## 目標
1. 維持 Phase 1/2 契約穩定，完成 Phase 3 文件化硬化。
2. 讓前後端可依欄位、錯誤、關聯、Practitioner 契約進行整合。

## 範圍
- M1：欄位字典
- M2：錯誤契約
- M3：關聯一致性與回應欄位說明
- M4：Practitioner 契約硬化第一步（list/create/edit）

## 非目標
- 不改壞既有 endpoint
- 不變更 `ok/data/error` 回應外形
- 不做破壞相容重構

## 里程碑

### M1（完成）
- [x] `docs/phase3-field-dictionary.md`

### M2（完成）
- [x] `docs/phase3-error-contract.md`

### M3（完成）
- [x] `docs/phase3-resource-linkage-contract.md`
- [x] `docs/phase3-facade-response-fields.md`

### M4（本輪完成）
- [x] `docs/phase3-practitioner-contract.md`
- [x] Practitioner list/create/edit 請求與回應欄位對齊文件
- [x] Practitioner not-found/validation 錯誤碼對齊文件

## 風險
1. 現況仍為 patient-level/latest 推論，非強一致快照。
2. conflict 類錯誤尚未全面逐端點落地。
3. Practitioner identifier 成對必填目前為寬鬆策略，需後續是否加嚴評估。

## 驗收標準
1. M1-M4 文件可對照現有 facade 行為。
2. Practitioner 契約可直接供前端串接與錯誤分支處理。
3. 文件已同步到 `fhir document/backend` 並索引可查。
