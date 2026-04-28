# PHASE3_PLAN

## 1) 目標（Goals）

1. 在維持既有 Phase 1/2 契約穩定前提下，完成可上線等級的後端整合能力。
2. 補齊 Phase 2 deferred 項目（錯誤分類精細化、自動化驗證、欄位命名凍結）。
3. 提升跨資源一致性（Condition / Media / DocumentReference / Practitioner）與可維運性。

## 2) 範圍（Scope）

1. 契約層
   - 鎖定並版控前後端欄位字典（payload/response）。
   - 補齊 domain conflict 類型錯誤碼（例如 `CONFLICT_ERROR`）與映射規則。
2. 驗證與品質
   - 將 Phase 2 smoke commands 腳本化（PowerShell）。
   - 建立可重複執行的 API 驗證流程（本機/CI）。
3. 資源一致性
   - 梳理 Practitioner 與 Condition/Observation/Media 的關聯欄位規範。
   - 補齊必要查詢與更新流程的一致輸出格式（不破壞既有 endpoint）。
4. 文件
   - 更新契約、錯誤碼、測試流程與封版清單文件。

## 3) 非目標（Non-Goals）

1. 不重寫或大幅重構既有 Phase 1/2 API 路徑。
2. 不在本計畫內新增與本產品無直接關聯的 FHIR 資源流程。
3. 不進行破壞性資料遷移或 destructive git 操作。
4. 不在此規劃文件中直接實作功能。

## 4) 里程碑（Milestones）

### M1：契約凍結與錯誤碼擴充

- 產出最終欄位字典（frontend/backend 對齊版）。
- 新增並文件化 conflict 類錯誤碼與判斷條件。
- 完成契約文件 review。

### M2：自動化驗證落地

- 將 smoke test 命令整併為可執行腳本。
- 補齊成功/失敗案例（validation、not-found、conflict、timeout）。
- 建立封版前標準檢查流程。

### M3：關聯一致性與封版就緒

- 完成 Practitioner 關聯欄位一致性檢查與文件回填。
- 完成跨資源輸出格式一致性驗證。
- 完成 Phase 3 封版檢查清單。

## 5) 風險（Risks）

1. 前後端欄位命名未及時凍結，導致重複映射與回歸成本增加。
2. 上游 HAPI 行為差異（search parameter / error diagnostics）影響 facade 穩定性。
3. 自動化測試覆蓋不足，造成封版前人工驗證負擔過高。
4. 新增錯誤碼若未同步前端處理，可能出現 UI 分支缺漏。

## 6) 驗收標準（Acceptance Criteria）

1. 契約文件
   - 有正式欄位字典版本與變更記錄。
   - Condition/Media/DocumentReference/Practitioner 皆有清楚 payload/response 規範。
2. 錯誤映射
   - not-found、validation、conflict、timeout/network 至少各有一個可重現案例。
   - facade 仍維持 `ok/data/error` 回應風格。
3. 自動化驗證
   - 一鍵執行 smoke script 可覆蓋主要路徑。
   - 驗證結果可作為封版依據。
4. 相容性
   - 既有 Phase 1/2 endpoint 契約不破壞。

## 7) 與前端契約策略（Frontend Contract Strategy）

1. 版本化契約
   - 以文件版號管理欄位字典與錯誤碼映射。
   - 每次契約變更附 migration note 與範例。
2. 穩定回應形狀
   - 持續使用 `ok/data/error` 包裝，避免前端解析分岔。
3. 先增量、後替換
   - 新欄位先 additive，保留舊欄位過渡期；移除須有公告窗口。
4. 雙向驗證
   - 前端提供使用情境，後端提供可重現 API 命令與預期結果。
5. 封版節奏
   - 封版前至少一次契約對齊會議，確認 deferred 是否轉入下一批或解除。
