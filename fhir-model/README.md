# FHIR 資源建模檔案

此資料夾提供你目前病歷欄位的可落地設計。

## 檔案說明

- `DATA_MODEL.md`：欄位到 FHIR 的映射規格
- `examples/patient-intake-bundle.json`：完整範例（Patient + Practitioner + CareTeam + Observation）
- `questionnaire/patient-intake-questionnaire.json`：可擴充欄位的問卷模板

## 建議使用順序

1. 先看 `DATA_MODEL.md`，確認欄位對應
2. 用 `patient-intake-bundle.json` 先建立一筆測試資料
3. 用 `patient-intake-questionnaire.json` 收未來不確定欄位
4. 欄位穩定後，再做 Profile/ValueSet 正式化

## 寫入範例

```powershell
$body = Get-Content .\fhir-model\examples\patient-intake-bundle.json -Raw

Invoke-RestMethod `
  -Uri "http://localhost:8091/fhir" `
  -Method Post `
  -ContentType "application/fhir+json" `
  -Body $body
```

如果在 auth 模式，請改走 `8090` 並帶 Bearer token。

## 一鍵匯入腳本（建議）

專案已提供：

- `scripts/import-intake-example.ps1`

### 開發模式匯入（直連 8091）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 -Mode dev
```

### 授權模式匯入（走 8090，自動拿 token）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 -Mode auth
```

你也可以自行傳 token：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 -Mode auth -AccessToken "<token>"
```

## 查詢病患匯入結果

專案已提供：

- `scripts/get-patient-intake.ps1`

### 用 Patient ID 查詢（開發模式）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-intake.ps1 -Mode dev -PatientId patient-001
```

### 用 National ID 查詢（授權模式）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-intake.ps1 -Mode auth -NationalId A123456789
```

### 輸出完整 JSON 檔

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-intake.ps1 -Mode auth -PatientId patient-001 -OutFile .\fhir-model\examples\patient-intake-query-result.json
```

## 部分欄位更新腳本

專案已提供：

- `scripts/update-patient-intake.ps1`

你可以只更新需要的欄位，不必整包重送。

### 範例：更新收入、興趣、行為模式（auth）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update-patient-intake.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -MonthlyIncome 88000 `
  -Hobby "Running, piano, travel" `
  -BehaviorPattern "Sleep late, irregular meals, moderate exercise"
```

### 範例：更新生物標記（HbA1c）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update-patient-intake.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -BiomarkerCode "4548-4" `
  -BiomarkerDisplay "Hemoglobin A1c/Hemoglobin.total in Blood" `
  -BiomarkerValue 6.8 `
  -BiomarkerUnit "%"
```

## 欄位變更歷程查詢

專案已提供：

- `scripts/get-patient-field-history.ps1`

### 查詢單一欄位歷程（hobby）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field hobby
```

### 查詢全部欄位歷程

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field all
```

### 匯出歷程 JSON

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field finance `
  -OutFile .\fhir-model\examples\patient-finance-history.json
```

### 匯出歷程 CSV（可直接開 Excel）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field all `
  -Order desc `
  -OutFormat csv `
  -OutFile .\fhir-model\examples\patient-history.csv
```

### 匯出中文欄位標題 CSV

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field all `
  -Order desc `
  -OutFormat csv `
  -CsvHeader zh-tw `
  -OutFile .\fhir-model\examples\patient-history-zh.csv
```

### 只看每個欄位最新 1 筆

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field all `
  -Latest 1
```

### 依時間區間過濾

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field hobby `
  -From "2026-04-23T00:00:00+08:00" `
  -To "2026-04-24T00:00:00+08:00"
```

### 以時間倒序顯示（最新在前）

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field hobby `
  -Order desc
```

### 包含刪除事件

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\get-patient-field-history.ps1 `
  -Mode auth `
  -PatientId patient-001 `
  -Field all `
  -IncludeDeleted
```

## �s�W�G�q JSON �إߧ���f���귽

�A�i�H�ϥ� `scripts/create-patient-intake.ps1`�A���@ JSON �ɸ�Ƥ@���إߦ��G
- `Patient`
- `Practitioner`�]�i��^
- `CareTeam`�]�i��^
- `Observation`�]�Ш|�{�סB¾�~�B����B����B�߲z�S�x�B�欰�Ҧ��B�ͪ��аO�BextraAttributes�^

�d�ҿ�J�ɡG`examples/patient-intake-input.sample.json`

### ����]dev�^
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create-patient-intake.ps1 `
  -Mode dev `
  -InputFile .\fhir-model\examples\patient-intake-input.sample.json
```

### ����]auth�^
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create-patient-intake.ps1 `
  -Mode auth `
  -InputFile .\fhir-model\examples\patient-intake-input.sample.json
```

## Definitions�]Profile/ValueSet�^

�s�W�ؿ��G`definitions/`
- `codesystem-patient-intake.json`
- `valueset-education-level.json`
- `structuredefinition-patient-intake-patient.json`
- `structuredefinition-patient-intake-observation.json`

�o���G
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-fhir-definitions.ps1 -Mode dev
```

���ҬJ���f����ơG
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-patient-intake.ps1 -Mode dev -PatientId patient-002
```

## Batch Import�]CSV�^

�s�W�}���G`scripts/import-patient-intake-csv.ps1`

�d�ҡG`examples/patient-intake-batch.sample.csv`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-patient-intake-csv.ps1 `
  -Mode dev `
  -CsvFile .\fhir-model\examples\patient-intake-batch.sample.csv
```

�פJ�����i�� `get-patient-intake.ps1` �P `validate-patient-intake.ps1` ���ҡC

## CSV Validation + Import Guard

�s�W�}���G`scripts/validate-patient-intake-csv.ps1`

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-patient-intake-csv.ps1 `
  -CsvFile .\fhir-model\examples\patient-intake-batch.invalid.sample.csv `
  -OutFile .\fhir-model\examples\patient-intake-batch.invalid.report.csv
```

`import-patient-intake-csv.ps1` �w��X�w�˻P���~�C���L�\��C

## Import Result Export

`import-patient-intake-csv.ps1` �䴩��X�G
- `-ImportResultCsvPath`
- `-ImportResultJsonPath`

JSON ���e�]�t�G
- `validationSummary`
- `importSummary`
- `results`
