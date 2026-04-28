# Phase 3 Resource Linkage Contract (M3 Minimal)

本文件定義目前後端 facade 可用的跨資源關聯欄位與查詢模式，供前端整合使用。

## 1. 契約範圍與原則

- 維持既有 `ok/data/error` 回應包裝。
- 不變更既有 endpoint 路徑。
- 僅描述目前可用關聯，未列者視為 deferred。

## 2. 可用關聯欄位（現況）

### Patient
- 主鍵：`Patient.id`
- 常用關聯：
  - `Patient.generalPractitioner[].reference -> Practitioner/{id}`

### Practitioner
- 主鍵：`Practitioner.id`
- 被參照位置：
  - `Patient.generalPractitioner[].reference`
  - `Condition.asserter.reference`（若 create payload 有 `asserterPractitionerId`）
  - `Media.operator.reference`（若 create payload 有 `operatorPractitionerId`）

### Observation
- 主鍵：`Observation.id`
- 關聯：
  - `Observation.subject.reference -> Patient/{id}`
- 查詢模式（目前 facade）：
  - 由病人彙整時讀取 `Observation?subject=Patient/{id}`

### Condition
- 主鍵：`Condition.id`
- 關聯：
  - `Condition.subject.reference -> Patient/{id}`
  - `Condition.asserter.reference -> Practitioner/{id}`（選填）
- 查詢模式（目前 facade）：
  - `GET /api/patients/{id}/conditions`（patient 過濾）
  - `GET /api/conditions/{id}`（單筆）

### DocumentReference
- 主鍵：`DocumentReference.id`
- 關聯：
  - `DocumentReference.subject.reference -> Patient/{id}`
- 查詢模式（目前 facade）：
  - `GET /api/patients/{id}/documents`（patient 過濾）

## 3. Query 模式與回應語意

### Patient-level Query（目前主流）
- `GET /api/patients/{id}/intake-summary`
- `GET /api/patients/{id}/conditions`
- `GET /api/patients/{id}/media`
- `GET /api/patients/{id}/documents`

特性：
- 以單一 patient 為資料邊界。
- `data.summary.*Count` 提供數量快照。
- 適合前端病例頁整合顯示。

### Latest 推論（現況）
- intake summary 屬於「patient-level 聚合」，不是 transaction 級資料快照。
- 若多資源非同一時間更新，前端看到的是「查詢當下最新可得狀態」。

## 4. 風險與限制（必讀）

1. **現況為 patient-level/latest 推論**
   - 風險：跨資源可能出現時間差，非強一致快照。
2. **關聯完整性依賴上游資料品質**
   - 例如 `Practitioner/{id}` 被參照但該資源不存在，會轉為 not-found 類錯誤。
3. **目前未提供跨病人全域關聯查詢契約**
   - 需要全域檢索時應另立 endpoint 與版本說明。

## 5. 與前端協作建議

1. 前端以 patient 為主索引，避免自行做跨病人關聯推導。
2. 先顯示主資料，再逐區塊渲染關聯資源，必要時容忍部分區塊 not-found。
3. 以 `error.code` 處理錯誤分支，不以 `message` 做邏輯判斷。
