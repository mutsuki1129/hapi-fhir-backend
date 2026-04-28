# PHASE2_TASKS

## 目標

在不破壞 Phase 1 契約的前提下，完成 Phase 2 後端最小可用能力，並具備可重現驗證文件，供封版使用。

## 契約守則

- 保持 Phase 1 Patient/Observation 既有流程不變。
- 保持 facade 回應格式穩定（`ok/data/error`）。
- 新增資源以增量方式交付，不重構既有路徑。

## Phase 2 實作狀態（封版）

### P0 Foundation

- [x] Phase 2 範圍與邊界確認
- [x] Phase 2 契約與重現命令文件建立
- [x] 錯誤映射擴充（Condition / Media / DocumentReference / Practitioner）

### P1 Condition

- [x] `POST /api/patients/{id}/conditions`
- [x] `GET /api/patients/{id}/conditions`
- [x] `GET /api/conditions/{id}`
- [x] 建立 payload 驗證（`clinicalStatus`、`codeText`/`code`）
- [x] 可選 `asserterPractitionerId` 關聯

### P2 Media / DocumentReference

- [x] `POST /api/patients/{id}/media`
- [x] `GET /api/patients/{id}/media`
- [x] `POST /api/patients/{id}/documents`
- [x] `GET /api/patients/{id}/documents`
- [x] 最小 metadata 契約（`contentType`、`url`、`title`/`description`）

### P3 Practitioner

- [x] `GET /api/practitioners`（含 `name` 查詢）
- [x] `POST /api/practitioners`
- [x] `PATCH /api/practitioners/{id}`
- [x] 與 Condition asserter 串接

### 文件與驗證

- [x] `PHASE2_FRONTEND_ENDPOINTS.md`
- [x] `docs/phase2-condition-contract.md`
- [x] `docs/phase2-smoke-test.md`
- [x] `OPERATIONOUTCOME_UI_MAPPING.md`（Phase 2 新資源錯誤碼）

## Deferred（保留至後續批次）

### D1. Domain conflict 錯誤分類細化

- 原因：本批次先完成可用 API 與穩定契約，衝突類型先以 `VALIDATION_ERROR` / `BAD_REQUEST` 表達。
- 風險：前端對重複/衝突情境提示粒度不足。
- Next step：新增 `CONFLICT_ERROR` 類型與對應判斷規則，回填契約文件。

### D2. 自動化測試腳本化

- 原因：目前提供可執行 smoke 指令，但未整合為單一自動化流程。
- 風險：回歸驗證依賴人工操作，封版前檢查成本較高。
- Next step：新增可重複執行的 PowerShell smoke script，並規劃接入 CI。

### D3. 前端欄位命名最終凍結

- 原因：需與前端共同確認最終畫面需求與欄位字典。
- 風險：若雙方命名認知不同，會增加映射補丁成本。
- Next step：與前端共同完成 payload/response 欄位字典鎖定並同步文件。
