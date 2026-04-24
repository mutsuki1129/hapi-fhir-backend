# 病歷資料 FHIR 資源設計（MVP）

本文件定義目前你提供的欄位，如何對應到 FHIR R4 資源。

## 1) 欄位對應總表

| 需求欄位 | FHIR 資源 | FHIR 欄位 | 備註 |
|---|---|---|---|
| 姓名 | Patient | `Patient.name` | `family` + `given` |
| 年齡 | Patient / Observation | `Patient.birthDate`（主要） | 年齡建議由生日計算；若只能提供年齡可用 Observation 暫存 |
| 性別 | Patient | `Patient.gender` | `male/female/other/unknown` |
| 教育程度 | Observation | `Observation.code` + `Observation.valueCodeableConcept` | 建議 category 用 `social-history` |
| 職業 | Observation | `Observation.code` + `Observation.valueString` | 可先用文字，後續再改碼表 |
| 收入與支出 | Observation | `Observation.component` | `income` / `expense`，單位建議 `TWD/month` |
| 興趣與愛好 | Observation | `Observation.valueString` | 可多筆 Observation 或一筆逗號分隔 |
| 心理特徵 | Observation | `Observation.valueString` | 可先做結構化文字 |
| 行為模式 | Observation | `Observation.valueString` | 例如作息、依從性、風險行為 |
| 生物標記 | Observation | `Observation.value[x]` | 如 HbA1c、CRP、BMI 等 |
| 治療醫師 | Practitioner / CareTeam | `Patient.generalPractitioner` 或 `CareTeam.participant` | 建議兩者都建 |
| 身分證 | Patient | `Patient.identifier` | 自訂 `system`，例如 `urn:tw:national-id` |
| 健保卡卡號 | Patient | `Patient.identifier` | 自訂 `system`，例如 `urn:tw:nhi-card` |

## 2) 建議最小資源集合

- `Patient`：病患主檔（姓名、性別、生日、識別碼）
- `Practitioner`：醫師主檔
- `CareTeam`：病患與主治醫師關聯
- `Observation`：教育、職業、收入支出、興趣、心理、行為、生物標記

## 3) 為什麼用 Observation 承接社會心理資料

- 可快速上線，不用一開始就設計大量 Extension
- 與 FHIR 生態相容，後續可逐步轉為標準碼
- 可保留時間戳（`effectiveDateTime`）與來源（`performer`）

## 4) Identifier system 建議

目前先採內部 URI（可後續替換）：

- 身分證：`urn:tw:national-id`
- 健保卡：`urn:tw:nhi-card`

## 5) 可擴充策略（你提到未來欄位不確定）

建議採「雙軌」：

1. 穩定欄位：持續放在固定資源欄位（Patient/Observation/CareTeam）
2. 變動欄位：透過 `Questionnaire` + `QuestionnaireResponse` 收集

這樣新欄位只要改問卷，不必立刻改資料庫 schema。

## 6) 下一步（建議）

1. 先用 `fhir-model/examples/patient-intake-bundle.json` 寫入一筆完整資料流程
2. 用 `fhir-model/questionnaire/patient-intake-questionnaire.json` 做前端動態問卷
3. 當欄位穩定後，再把常用欄位做成 Profile/ValueSet（Implementation Guide）
