# FHIR Server（HAPI FHIR）

本專案從 0 開始建置 FHIR Server，基於 HAPI FHIR，並提供：
- Docker 一鍵啟動（dev / auth 兩種模式）
- 病歷資料模型（Patient / Observation / Practitioner / CareTeam）
- JSON 建立病歷、更新、查詢、歷史追蹤
- CSV 批次匯入（含驗證、錯誤報表、匯入結果報表）
- Profile / ValueSet / CodeSystem 發布與 `$validate`
- 簡易 Web UI 上傳 CSV

## Backend stack and versions

- FHIR version: R4 (`4.0.1`)
- HAPI FHIR image: `hapiproject/hapi@sha256:34c86fd5805df77c2b9d9c10538050b16ac3dc244352da0ebe4717f931330775`
- HAPI FHIR release tracked by Phase 1 docs: `8.8.0`
- Database: PostgreSQL 16
- Optional auth: Keycloak `26.1.5` and oauth2-proxy `v7.8.1`
- Phase 1 facade: Python `http.server` wrapper in `scripts/import_ui_server.py`

## 0. Repo baseline / Phase 1 邊界

- 目前目錄可直接作為專案工作區使用，但本機可能尚未初始化為 git repo；請不要在未確認團隊流程前自行 `git init` 或設定 remote。
- Phase 1 backend 範圍：基線文件、HAPI FHIR dev/auth 啟動、Patient + Observation 既有能力、Phase 1 facade、CORS、OperationOutcome 錯誤映射與測試資料。
- Phase 1 不實作：`Condition`、`Media` / `DocumentReference`、Practitioner CRUD 或 Practitioner 頁面流程。
- 若文件提到 `Practitioner` / `CareTeam`，在 Phase 1 僅代表既有 intake summary 的關聯讀取或既有資料模型脈絡，不代表新增 Phase 2 workflow。

## Phase 1 facade API

Default facade base URL: `http://127.0.0.1:8092`

- `GET /health`
- `GET /api/patients/{id}/intake-summary`
- `POST /api/patients/intake`
- `PATCH /api/patients/{id}/intake`
- `POST /api/process` for the existing CSV import UI compatibility path

All facade responses use a stable `ok/data/error` envelope. Error details are documented in `OPERATIONOUTCOME_UI_MAPPING.md` and `docs/phase1-frontend-error-smoke-test.md`.

## 1. 技術架構

- FHIR Server：HAPI FHIR JPA Server（R4）
- Database：PostgreSQL
- 驗證與授權（可選）：Keycloak + OAuth2 Proxy
- 開發環境：Docker Compose + PowerShell 腳本

## 2. 專案啟動

### 2.1 準備環境

```powershell
Copy-Item .env.example .env
```

### 2.1.1 Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `SPRING_PROFILES_ACTIVE` | `dev` | HAPI Spring profile. Use `dev` locally; append auth profile only when needed. |
| `COMPOSE_PROFILES` | empty | Enables optional Compose profiles such as auth services. |
| `POSTGRES_DB` | `hapi` | PostgreSQL database name. |
| `POSTGRES_USER` | `hapi` | PostgreSQL username. |
| `POSTGRES_PASSWORD` | `hapi_pw` | PostgreSQL password for local dev. |
| `FHIR_JWT_ISSUER_URI` | `http://keycloak:8180/realms/fhir` | Issuer URL for auth-mode JWT validation. |
| `KEYCLOAK_ADMIN` | `admin` | Local Keycloak admin user. |
| `KEYCLOAK_ADMIN_PASSWORD` | `admin123` | Local Keycloak admin password. |
| `OAUTH2_PROXY_COOKIE_SECRET` | local sample value | oauth2-proxy cookie secret for auth mode. |

Do not commit `.env`; keep committed defaults in `.env.example`.

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

## Phase 1 known limitations

- HAPI native responses can still be raw FHIR `OperationOutcome`; the UI-facing stable envelope is provided by the Phase 1 facade.
- CORS is explicit at the facade layer. HAPI native CORS remains a separate deployment concern for non-facade clients.
- Network failure and timeout are normalized by the facade as `NETWORK_ERROR` and `TIMEOUT` for frontend hardening.
- `Condition`, `Media`, `DocumentReference`, and Practitioner workflow implementation are deferred to later phases.
- The local folder currently may not be initialized as a git repository; confirm team git workflow before making commits.

## Documents

- Backend docs index: `docs/README.md`
- Repo baseline inventory: `docs/repo-baseline.md`
- Frontend hardening matrix: `docs/phase1-frontend-error-smoke-test.md`
- Facade contract: `PHASE1_FRONTEND_ENDPOINTS.md`
- Error mapping: `OPERATIONOUTCOME_UI_MAPPING.md`
- Server capability snapshot: `SERVER_CAPABILITY.md`
- Phase 1 backend gaps: `BACKEND_GAPS_FOR_PHASE1.md`
- Canonical shared project/backend docs: `C:\Users\clamp\Desktop\project\fhir document\common\project\*.md` and `C:\Users\clamp\Desktop\project\fhir document\common\backend\*.md`

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
