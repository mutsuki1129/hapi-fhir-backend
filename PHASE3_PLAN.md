# PHASE3_PLAN

## 目標
1. 在不破壞 Phase 1/2 契約前提下，凍結後端欄位字典並建立可演進規則。
2. 補齊跨資源（Patient / Practitioner / Observation / Condition / DocumentReference）契約對照與錯誤映射。
3. 讓前後端在 Phase 3 開發期間以穩定 `ok/data/error` 介面協作。

## 範圍
- 文件與契約層工作（欄位字典、錯誤碼、變更策略、待辦收斂）。
- 既有 facade API 行為對齊與說明，不新增破壞性改動。
- 延續 `fhir-model/examples/patient-intake-bundle.json` 作為欄位語意基準。

## 非目標
- 不重寫 Phase 1/2 現有 API。
- 不做破壞相容的欄位改名或刪除。
- 不在本階段導入大規模資料搬遷。

## 里程碑

### M1（已完成，後端）
- [x] 新增 `docs/phase3-field-dictionary.md`，凍結主要資源欄位字典。
- [x] 納入錯誤碼映射與前端可用欄位變更策略（additive first / deprecation window / version note）。
- [x] 同步更新 Phase 3 待辦狀態（`待辦事項/Phase 3/backend-待辦.md`）。

### M2（待執行）
- [ ] 依欄位字典補 smoke 測試樣本（成功/驗證失敗/not-found）。
- [ ] 針對跨資源關聯補最小一致性檢核（病人、醫師、條件、文件）。

### M3（待執行）
- [ ] 版本註記流程常態化（每次契約變更附日期與相容性說明）。
- [ ] 封版前完成 deferred 項目風險再評估與交接說明。

## 風險
1. 各環境 HAPI 回傳 diagnostics 細節不同，可能影響錯誤碼判斷穩定度。
2. 若前端以文案而非 `error.code` 分支，契約演進風險升高。
3. 跨資源關聯資料若未統一命名與格式，會放大整合成本。

## 驗收標準
1. 欄位字典可直接對應現有 facade payload/response。
2. 主要錯誤碼可由前端穩定使用（至少 `VALIDATION_ERROR` / `*_NOT_FOUND` / `NETWORK_ERROR` / `TIMEOUT`）。
3. 待辦文件清楚標示完成、deferred 與下一步。

## 與前端契約策略
1. Additive first：先加欄位、不刪欄位。
2. Deprecation window：淘汰欄位需保留觀察期並提供替代方案。
3. Version note：每次契約變更需附日期、摘要、相容性影響。
4. 前端錯誤處理以 `error.code` 為主，`message` 僅作顯示。
