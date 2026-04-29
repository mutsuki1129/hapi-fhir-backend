# Phase X DATA_MODEL Alignment (Backend)

更新日期：2026-04-29

## 1) 對齊來源

- `fhir-model/DATA_MODEL.md`
- 既有 facade：`GET /api/patients/{id}/intake-summary`

## 2) 本輪後端對齊（additive，不破壞既有契約）

在 `intake-summary` 回應新增：
- `modelAlignment.patient.birthDate`
- `modelAlignment.patient.age`（由 `birthDate` 推導）
- `modelAlignment.patient.identifiers.nationalId`
- `modelAlignment.patient.identifiers.nhiCardNo`
- `modelAlignment.observation.*`
  - `educationLevel`
  - `occupation`
  - `monthlyIncome`
  - `monthlyExpense`
  - `hobby`
  - `psychologicalTraits`
  - `behaviorPattern`
  - `biomarker`（code/display/system/value/unit）
- `modelAlignment.doctor`
  - `practitionerId`
  - `name`

## 3) DATA_MODEL 對應摘要

1. 年齡：由 `Patient.birthDate` 即時計算，無額外寫入資源。
2. 身分證/健保卡：
   - `urn:tw:national-id` -> `nationalId`
   - `urn:tw:nhi-card` -> `nhiCardNo`
3. 社會心理與生物標記：由 Observation code/value 映射穩定回傳。
4. 治療醫師：
   - 來源為 `Patient.generalPractitioner` + CareTeam 參照鏈可取得的 Practitioner。
   - 先回傳主醫師摘要於 `modelAlignment.doctor`，保留原本 `data.practitioners[]`。

## 4) 相容性說明

- 既有 `ok/data/error`、原 `data` 區塊不變。
- 新欄位皆為 additive，舊前端不受影響。

## 5) 驗證命令

```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/intake-summary?mode=dev"
```

驗證重點：
- `modelAlignment.patient.age` 有值
- `modelAlignment.patient.identifiers` 正確映射
- `modelAlignment.observation` 各欄位可穩定取得
- `modelAlignment.doctor.practitionerId` 可取得
