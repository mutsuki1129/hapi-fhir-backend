# FHIR Server（HAPI FHIR）

本專案從 0 開始建置 FHIR Server，基於 HAPI FHIR，並提供：
- Docker 一鍵啟動（dev / auth 兩種模式）
- 病歷資料模型（Patient / Observation / Practitioner / CareTeam）
- JSON 建立病歷、更新、查詢、歷史追蹤
- CSV 批次匯入（含驗證、錯誤報表、匯入結果報表）
- Profile / ValueSet / CodeSystem 發布與 `$validate`
- 簡易 Web UI 上傳 CSV

## 後端技術棧與版本

- FHIR 版本：R4（`4.0.1`）
- HAPI FHIR 映像：`hapiproject/hapi@sha256:34c86fd5805df77c2b9d9c10538050b16ac3dc244352da0ebe4717f931330775`
- Phase 1 文件追蹤的 HAPI FHIR 版本：`8.8.0`
- 資料庫：PostgreSQL 16
- 可選驗證授權：Keycloak `26.1.5` 與 oauth2-proxy `v7.8.1`
- Phase 1 facade：位於 `scripts/import_ui_server.py` 的 Python `http.server` 包裝層

## 0. Repo 基線 / Phase 1 邊界

- 目前目錄可直接作為專案工作區使用，但本機可能尚未初始化為 git repo；請不要在未確認團隊流程前自行 `git init` 或設定 remote。
- Phase 1 backend 範圍：基線文件、HAPI FHIR dev/auth 啟動、Patient + Observation 既有能力、Phase 1 facade、CORS、OperationOutcome 錯誤映射與測試資料。
- Phase 1 不實作：`Condition`、`Media` / `DocumentReference`、Practitioner CRUD 或 Practitioner 頁面流程。
- 若文件提到 `Practitioner` / `CareTeam`，在 Phase 1 僅代表既有 intake summary 的關聯讀取或既有資料模型脈絡，不代表新增 Phase 2 workflow。

## Phase 1 facade API

預設 facade base URL：`http://127.0.0.1:8092`

- `GET /health`
- `GET /api/patients/{id}/intake-summary`
- `POST /api/patients/intake`
- `PATCH /api/patients/{id}/intake`
- `POST /api/process`：供既有 CSV 匯入 UI 的相容路徑使用

所有 facade 回應皆使用穩定的 `ok/data/error` 包裝格式。錯誤細節文件請見 `OPERATIONOUTCOME_UI_MAPPING.md` 與 `docs/phase1-frontend-error-smoke-test.md`。

## 1. 技術架構

- FHIR Server：HAPI FHIR JPA Server（R4）
- 資料庫：PostgreSQL
- 驗證與授權（可選）：Keycloak + OAuth2 Proxy
- 開發環境：Docker Compose + PowerShell 腳本

## 2. 專案啟動

### 2.1 準備環境

```powershell
Copy-Item .env.example .env
```

### 2.1.1 環境變數

| 變數 | 預設值 | 用途 |
| --- | --- | --- |
| `SPRING_PROFILES_ACTIVE` | `dev` | HAPI Spring profile。本機開發使用 `dev`；僅在需要時再附加 auth profile。 |
| `COMPOSE_PROFILES` | 空值 | 啟用可選的 Compose profiles（例如 auth 服務）。 |
| `POSTGRES_DB` | `hapi` | PostgreSQL 資料庫名稱。 |
| `POSTGRES_USER` | `hapi` | PostgreSQL 使用者名稱。 |
| `POSTGRES_PASSWORD` | `hapi_pw` | 本機開發用 PostgreSQL 密碼。 |
| `FHIR_JWT_ISSUER_URI` | `http://keycloak:8180/realms/fhir` | auth 模式 JWT 驗證用的 issuer URL。 |
| `KEYCLOAK_ADMIN` | `admin` | 本機 Keycloak 管理者帳號。 |
| `KEYCLOAK_ADMIN_PASSWORD` | `admin123` | 本機 Keycloak 管理者密碼。 |
| `OAUTH2_PROXY_COOKIE_SECRET` | 本機範例值 | auth 模式下 oauth2-proxy 的 cookie secret。 |

請勿提交 `.env`；可提交的預設值應保留在 `.env.example`。

### 2.2 dev 模式（直接打 HAPI）

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

健康檢查：

```powershell
curl http://localhost:8091/actuator/health
```

FHIR metadata：

```powershell
curl http://localhost:8091/fhir/metadata
```

### 2.3 auth 模式（經過 Proxy + Token）

```powershell
docker compose -f docker-compose.yml -f docker-compose.auth.yml up -d
```

預設入口：
- FHIR（Proxy）：`http://localhost:8090`
- Keycloak：`http://localhost:8180`

## 3. 常用腳本

## 3.1 匯入範例 Bundle

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 -Mode dev
```

## 3.2 查詢病人整包資料

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-intake.ps1 -Mode dev -PatientId patient-001
```

## 3.3 更新病歷欄位

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update-patient-intake.ps1 -Mode dev -PatientId patient-001 -MonthlyIncome 88000
```

## 3.4 查詢欄位歷史

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 -Mode dev -PatientId patient-001 -Field all
```

## 4. 用 JSON 建立完整病歷

範例檔：`fhir-model/examples/patient-intake-input.sample.json`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create-patient-intake.ps1 `
  -Mode dev `
  -InputFile .\fhir-model\examples\patient-intake-input.sample.json
```

## 5. 發布 FHIR 定義（Profile / ValueSet / CodeSystem）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-fhir-definitions.ps1 -Mode dev
```

定義目錄：`fhir-model/definitions`

## 6. 驗證資料（$validate）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-patient-intake.ps1 `
  -Mode dev `
  -PatientId patient-002
```

## 7. CSV 批次匯入

範例檔：`fhir-model/examples/patient-intake-batch.sample.csv`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-patient-intake-csv.ps1 `
  -Mode dev `
  -CsvFile .\fhir-model\examples\patient-intake-batch.sample.csv
```

## 7.1 只做 CSV 驗證

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-patient-intake-csv.ps1 `
  -CsvFile .\fhir-model\examples\patient-intake-batch.sample.csv `
  -OutFile .\fhir-model\examples\patient-intake-batch.report.csv
```

## 7.2 匯入前預檢（整合在匯入腳本）

- `-ValidateOnly`：只驗證不匯入
- `-ContinueOnValidationError`：跳過錯誤列，匯入有效列
- `-ValidationReportPath`：輸出驗證報表
- `-ImportResultCsvPath`：輸出逐列匯入結果
- `-ImportResultJsonPath`：輸出完整摘要 JSON

範例：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-patient-intake-csv.ps1 `
  -Mode dev `
  -CsvFile .\fhir-model\examples\patient-intake-batch.invalid.sample.csv `
  -ContinueOnValidationError `
  -ValidationReportPath .\fhir-model\examples\patient-intake-batch.invalid.report.csv `
  -ImportResultCsvPath .\fhir-model\examples\patient-intake-batch.invalid.import-result.csv `
  -ImportResultJsonPath .\fhir-model\examples\patient-intake-batch.invalid.import-result.json
```

## 8. Web UI（CSV 上傳）

啟動：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092
```

開啟：
- `http://127.0.0.1:8092/`
- `http://127.0.0.1:8092/health`

功能：
- 上傳 CSV
- 只做驗證
- 驗證後匯入
- 顯示驗證問題與匯入結果

## 9. 停止服務

```powershell
docker compose down
```

清除資料庫 volume：

```powershell
docker compose down -v
```

## Phase 1 後端能力（Patient + Observation）

- Facade 服務：`scripts/start-import-ui.ps1`
- Endpoint 契約：`PHASE1_FRONTEND_ENDPOINTS.md`
- 錯誤映射：`OPERATIONOUTCOME_UI_MAPPING.md`
- 測試資料：
  - `fhir-model/examples/phase1-intake-create.sample.json`
  - `scripts/seed-phase1-test-data.ps1`

## Phase 1 已知限制

- HAPI 原生回應仍可能是原始 FHIR `OperationOutcome`；提供給 UI 的穩定包裝格式由 Phase 1 facade 負責。
- CORS 目前在 facade 層明確處理。對非 facade 客戶端而言，HAPI 原生 CORS 仍屬獨立部署議題。
- 網路失敗與逾時在 facade 層會被正規化為 `NETWORK_ERROR` 與 `TIMEOUT`，用於前端硬化。
- `Condition`、`Media`、`DocumentReference` 與 Practitioner workflow 實作延後至後續階段。
- 本機資料夾目前可能尚未初始化為 git repository；提交前請先確認團隊 git 流程。

## 文件

- 後端文件索引：`docs/README.md`
- Repo 基線盤點：`docs/repo-baseline.md`
- 前端硬化測試矩陣：`docs/phase1-frontend-error-smoke-test.md`
- Facade 契約：`PHASE1_FRONTEND_ENDPOINTS.md`
- 錯誤映射：`OPERATIONOUTCOME_UI_MAPPING.md`
- Server 能力快照：`SERVER_CAPABILITY.md`
- Phase 1 後端缺口：`BACKEND_GAPS_FOR_PHASE1.md`
- 共享的 project/backend 正典文件：`C:\Users\clamp\Desktop\project\fhir document\common\project\*.md` 與 `C:\Users\clamp\Desktop\project\fhir document\common\backend\*.md`

## Phase 1 hardening 驗收命令

```powershell
python -m py_compile .\scripts\import_ui_server.py
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

```powershell
curl http://localhost:8091/actuator/health
curl http://localhost:8091/fhir/metadata
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-import-ui.ps1 -Port 8092 -CorsOrigin "*"
curl http://127.0.0.1:8092/health
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed-phase1-test-data.ps1 -Mode dev
curl "http://127.0.0.1:8092/api/patients/phase1-patient-001/intake-summary?mode=dev"
```
