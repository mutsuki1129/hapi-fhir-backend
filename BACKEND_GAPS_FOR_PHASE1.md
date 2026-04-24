# BACKEND_GAPS_FOR_PHASE1

## 文件目的

盤點「第一階段（Patient + Observation 優先）」時，前端最容易卡住的後端缺口，並給出建議優先順序。

## 優先級定義

- P0：不補會直接阻塞前端主流程
- P1：不補可勉強上線，但成本高、風險高
- P2：優化項，建議在 P0/P1 後完成

## 缺口清單

## 狀態總覽（本次更新）

- P0-1 API Facade：`已完成（Phase 1 最小版）`
- P0-2 CORS：`已完成（Facade 層）`
- P0-3 OperationOutcome 錯誤映射：`已完成（Facade 層）`
- 其餘 P1/P2：`待完成`

## 1) P0 - 缺少前端導向的 API Facade（聚合端點）

現況：
- 已提供 Phase 1 facade endpoint（見 `PHASE1_FRONTEND_ENDPOINTS.md`）。

前端痛點：
- 多請求串接複雜、錯誤處理分散、性能不可控。

建議：
- 提供 Phase 1 專用 API：
  - `GET /api/patients/{id}/intake-summary`
  - `POST /api/patients/intake`
  - `PATCH /api/patients/{id}/intake`
  - `GET /api/patients/{id}/history?field=...`

## 2) P0 - CORS 未明確設定

現況：
- HAPI 原生回應仍未帶 CORS header（實測為空）。
- Phase 1 facade 已補 CORS header（可調整 allow-origin）。

前端痛點：
- 前後端跨網域時，瀏覽器請求會被擋。

建議：
- 在 HAPI 或反向代理層明確設定 CORS 白名單（dev/staging/prod 分環境）。

## 3) P0 - 錯誤格式尚未完成 UI 友善映射

現況：
- HAPI 錯誤仍為 FHIR `OperationOutcome`。
- Phase 1 facade 已提供 UI 錯誤碼映射（見 `OPERATIONOUTCOME_UI_MAPPING.md`）。

前端痛點：
- 需自行解析 `issue[]`，難以穩定映射成使用者可理解訊息。

建議：
- 建立後端錯誤映射規則：
  - `OperationOutcome.issue.code` -> 前端錯誤代碼（例如 `PATIENT_NOT_FOUND`）
  - `diagnostics` -> 可讀訊息（可中英文）

## 4) P1 - 認證流程對前端不夠完整

現況：
- auth 模式已有 Keycloak + OAuth2 Proxy，但偏後端/腳本操作。

前端痛點：
- 缺少明確登入、token 續期、登出、權限失效處理流程。

建議：
- 定義前端整合流程（OIDC code flow 或由 BFF 代管 token）。

## 5) P1 - Search/Sort/Pagination 契約未收斂

現況：
- FHIR 原生支援 `_count` 與 `link.next`，但前端頁面契約尚未統一。

前端痛點：
- 各頁面自行解析 bundle，重工高。

建議：
- API Facade 統一回傳：
  - `items[]`
  - `page.nextToken`（封裝 FHIR next URL）
  - `total`（可選）

## 6) P1 - 必填欄位驗證規則雖有，但回報一致性不足

現況：
- 有 Profile 與 CSV 驗證腳本。

前端痛點：
- API 層與批次層錯誤回報格式不一致，前端要寫兩套。

建議：
- 定義單一 validation error schema（欄位、錯誤碼、建議修正）。

## 7) P2 - 術語系統仍以本地 lite code system 為主

現況：
- biomarker 目前可使用 local `biomarker-lite` code system。

前端痛點：
- 後續若要與外部資料對接，code 對齊成本高。

建議：
- 規劃接軌 LOINC/SNOMED（至少建立對照表與轉換策略）。

## 8) P2 - 匯入任務缺少可追蹤的 Job 模型

現況：
- 已有 CSV/JSON 報表，但以腳本執行為主。

前端痛點：
- 難做長任務進度條、重試、歷史查詢。

建議：
- 增加匯入 job API：建立任務、查詢進度、查詢結果、下載報表。

## 建議實作順序

1. P0：API Facade + CORS + 錯誤映射
2. P1：認證流程契約 + 分頁契約 + 驗證回報一致化
3. P2：術語接軌 + 匯入任務化
