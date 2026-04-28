# PHASE3_PLAN

## 目標
1. 維持 Phase 1/2 契約穩定，完成 Phase 3 文件化與可演進規範。
2. 釐清欄位字典與錯誤碼契約，讓前後端可同步開發。
3. 以最小風險方式補強 M2：錯誤分類策略與驗證路徑說明。

## 範圍
- 欄位字典凍結（M1）
- 錯誤契約與分類策略（M2）
- 待辦與 deferred 風險管理

## 非目標
- 不改壞既有 endpoint 路徑與 `ok/data/error` 包裝
- 不做破壞相容欄位變更
- 不新增 Phase 3 功能實作（本批次以契約文件為主）

## 里程碑

### M1（已完成）
- [x] `docs/phase3-field-dictionary.md`
- [x] 欄位變更策略（additive first / deprecation window / version note）
- [x] 同步 Phase 3 backend 待辦

### M2（本輪完成）
- [x] `docs/phase3-error-contract.md`（validation / not-found / conflict / timeout）
- [x] 錯誤碼策略與 `ok/data/error` 一致性文件化
- [x] 更新 Phase 3 backend 待辦（完成/未完成與風險）

### M3（待執行）
- [ ] 補完整 smoke 測試矩陣（成功/驗證失敗/not-found/timeout）
- [ ] 補跨資源回歸檢查清單（Patient/Practitioner/Condition/Media/DocumentReference）

## 風險
1. 不同 HAPI 環境 diagnostics 文字可能不同，影響細部映射判斷。
2. 若前端使用 `message` 作流程分支，會提高契約變更風險。
3. conflict 類錯誤目前以策略保留為主，需後續逐端點落地。

## 驗收標準
1. M1/M2 文件可直接對照現有 facade 行為。
2. 錯誤分類至少覆蓋 validation / not-found / conflict / timeout。
3. `待辦事項/Phase 3/backend-待辦.md` 完整標示已完成與 deferred 項目。

## 與前端契約策略
1. Additive first：先加不刪。
2. Deprecation window：淘汰欄位需有過渡期。
3. Version note：每次變更需記錄日期、摘要、相容性影響。
