# PROJECT_BRIEF

## 專案目標

建立可落地的 FHIR Server 開發基礎，支援病歷資料建模、驗證、批次匯入與基本操作介面，方便快速進入 PoC 與後續擴充。

## 已完成範圍

- HAPI FHIR + PostgreSQL 基礎環境
- dev / auth 雙模式 Docker 啟動
- 病歷資料模型（Patient / Observation / Practitioner / CareTeam）
- JSON 建立與更新病歷腳本
- 歷史查詢與欄位追蹤腳本
- FHIR 定義發布：CodeSystem / ValueSet / StructureDefinition
- `$validate` 驗證流程
- CSV 驗證、錯誤報表、批次匯入
- 匯入結果報表（CSV + JSON）
- Web UI 上傳 CSV（驗證與匯入）

## 目前可直接使用的能力

1. 啟動服務（dev/auth）
2. 建立與查詢病歷資料
3. 批次匯入 CSV（可選擇遇錯中止或跳過錯誤列）
4. 產出驗證與匯入報表，利於稽核與追蹤
5. 用瀏覽器操作匯入流程（非工程人員可用）

## 主要腳本

- `scripts/create-patient-intake.ps1`
- `scripts/get-patient-intake.ps1`
- `scripts/update-patient-intake.ps1`
- `scripts/get-patient-field-history.ps1`
- `scripts/publish-fhir-definitions.ps1`
- `scripts/validate-patient-intake.ps1`
- `scripts/validate-patient-intake-csv.ps1`
- `scripts/import-patient-intake-csv.ps1`
- `scripts/start-import-ui.ps1`

## 關鍵文件

- `README.md`
- `PROJECT_OVERVIEW.md`
- `fhir-model/DATA_MODEL.md`
- `fhir-model/README.md`

## 下一步建議

1. 將 CSV 驗證規則外部化（例如 JSON 設定檔），便於維護。
2. 新增角色權限與審計日誌（誰匯入、何時匯入、匯入結果）。
3. 建立 CI 流程，自動執行腳本 smoke test 與 FHIR 驗證。
4. 規劃 staging / production 的部署與備援策略。
