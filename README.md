# FHIR Server（HAPI FHIR）

本專案以 HAPI FHIR R4 為核心，提供可在本機快速啟動的後端環境與 Phase 1/Phase 2 漸進式 facade API。

目前已落地能力包含：
- Docker 一鍵啟動（`dev` / `auth`）
- 病歷核心資料（Patient、Observation）建立/更新/查詢
- CSV 匯入與驗證（含報表）
- FHIR 定義發布與 `$validate`
- Phase 1 facade（穩定 `ok/data/error` 回應）
- Phase 2 第一批：Condition 最小可用 create/read/list by patient

## 後端技術棧與版本

- FHIR 版本：R4（`4.0.1`）
- HAPI FHIR 映像：`hapiproject/hapi@sha256:34c86fd5805df77c2b9d9c10538050b16ac3dc244352da0ebe4717f931330775`
- HAPI 版本（Phase 文件追蹤）：`8.8.0`
- 資料庫：PostgreSQL 16
- 可選認證：Keycloak `26.1.5` + oauth2-proxy `v7.8.1`
- Facade：`scripts/import_ui_server.py`（Python `http.server`）

## 0. 範圍邊界

### Phase 1 已完成重點

- HAPI FHIR dev/auth 啟動
- Patient + Observation 主流程
- facade CORS、OperationOutcome 錯誤映射
- `GET/POST/PATCH` intake 流程
- Observation-only delete（不刪 Patient）

### Phase 2 目前批次（已完成）

- Condition 最小可用流程（create/read/list）
- 保持既有 Phase 1 endpoint 契約不破壞

### Phase 2 尚未完成

- Media / DocumentReference facade 流程
- Practitioner 工作流（列表/建立/編輯）與 Condition/Observation 關聯強化

## 1. 基本啟動

### 1.1 準備環境

```powershell
Copy-Item .env.example .env
```

> `.env` 不提交；可提交預設值維持在 `.env.example`。

### 1.2 啟動 dev（直連 HAPI）

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

健康檢查：

```powershell
curl http://localhost:8091/actuator/health
curl http://localhost:8091/fhir/metadata
```

### 1.3 啟動 auth（經 Proxy）

```powershell
docker compose -f docker-compose.yml -f docker-compose.auth.yml up -d
```

預設入口：
- FHIR（Proxy）：`http://localhost:8090`
- Keycloak：`http://localhost:8180`

### 1.4 啟動 facade

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
```

```powershell
curl http://127.0.0.1:8092/health
```

## 2. Phase 1 Facade API

Base URL：`http://127.0.0.1:8092`

- `GET /health`
- `GET /api/patients/{id}/intake-summary`
- `POST /api/patients/intake`
- `PATCH /api/patients/{id}/intake`
- `DELETE /api/patients/{id}/intake`（僅刪 Observation，不刪 Patient）
- `POST /api/process`（既有 CSV UI 相容路徑）

## 3. Phase 2 Facade API（Condition MVP）

- `POST /api/patients/{id}/conditions`
- `GET /api/patients/{id}/conditions`
- `GET /api/conditions/{id}`

回應格式沿用既有 facade 風格：

```json
{
  "ok": true,
  "data": {},
  "source": {}
}
```

錯誤格式：

```json
{
  "ok": false,
  "error": {
    "code": "CONDITION_NOT_FOUND",
    "message": "Condition was not found.",
    "httpStatus": 404
  }
}
```

## 4. 常用腳本（維持）

### 4.1 建立 intake 範例

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create-patient-intake.ps1 `
  -Mode dev `
  -InputFile .\fhir-model\examples\patient-intake-input.sample.json
```

### 4.2 匯入 Bundle

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 -Mode dev
```

### 4.3 更新 intake

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update-patient-intake.ps1 -Mode dev -PatientId patient-001 -MonthlyIncome 88000
```

### 4.4 CSV 匯入

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-patient-intake-csv.ps1 `
  -Mode dev `
  -CsvFile .\fhir-model\examples\patient-intake-batch.sample.csv
```

### 4.5 CSV 驗證

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-patient-intake-csv.ps1 `
  -CsvFile .\fhir-model\examples\patient-intake-batch.sample.csv `
  -OutFile .\fhir-model\examples\patient-intake-batch.report.csv
```

## 5. Phase 2 Condition 最小驗證命令

```powershell
curl.exe -sS -X POST "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\",\"code\":{\"system\":\"http://snomed.info/sct\",\"code\":\"38341003\",\"display\":\"Hypertensive disorder, systemic arterial (disorder)\"},\"clinicalStatus\":\"active\",\"verificationStatus\":\"confirmed\",\"categoryCode\":\"problem-list-item\",\"categoryText\":\"Problem List Item\",\"onsetDateTime\":\"2026-04-28T09:10:00+08:00\",\"note\":\"Phase 2 minimum condition sample\"}}"
```

```powershell
curl.exe -sS "http://127.0.0.1:8092/api/patients/phase1-patient-001/conditions?mode=dev"
```

## 6. 文件索引

- Phase 1 endpoint 契約：`PHASE1_FRONTEND_ENDPOINTS.md`
- Phase 2 endpoint 契約：`PHASE2_FRONTEND_ENDPOINTS.md`
- 錯誤映射：`OPERATIONOUTCOME_UI_MAPPING.md`
- 伺服器能力盤點：`SERVER_CAPABILITY.md`
- Phase 1 缺口：`BACKEND_GAPS_FOR_PHASE1.md`
- Phase 2 工作清單：`PHASE2_TASKS.md`
- Phase 2 Condition 設計：`PHASE2_CONDITION_PLAN.md`
- Repro 文件：
  - `docs/phase1-frontend-error-smoke-test.md`
  - `docs/phase1-observation-delete-repro.md`
  - `docs/phase2-condition-repro.md`

## 7. 停止服務

```powershell
docker compose down
```

清除資料庫 volume：

```powershell
docker compose down -v
```
