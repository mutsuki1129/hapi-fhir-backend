# Phase 3 Field Dictionary (M1 Freeze)

本文件凍結 Phase 3 M1 後端欄位契約基線。來源依據：
- `scripts/import_ui_server.py`（facade API 實作）
- `fhir-model/examples/patient-intake-bundle.json`（FHIR 資料基準）
- `OPERATIONOUTCOME_UI_MAPPING.md`（錯誤碼映射）

## 1. 共用回應包裝（Facade）

成功：

```json
{
  "ok": true,
  "data": {},
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091",
    "resourceType": ["Patient"]
  }
}
```

失敗：

```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Submitted data is invalid. Please review the request.",
    "httpStatus": 400
  }
}
```

## 2. Patient

### 2.1 FHIR 欄位（基線）
| FHIR 欄位 | Facade payload/response 欄位 | 必填 | 說明 |
| --- | --- | --- | --- |
| `Patient.id` | `data.patient.id` | 回應必有 | 病人 ID |
| `Patient.name[0].family` | `payload.patient.family` / `data.patient.name[].family` | 建立時建議填 | 姓氏 |
| `Patient.name[0].given[]` | `payload.patient.given` / `data.patient.name[].given[]` | 建立時建議填 | 名字 |
| `Patient.gender` | `payload.patient.gender` / `data.patient.gender` | 選填 | 性別 |
| `Patient.birthDate` | `payload.patient.birthDate` / `data.patient.birthDate` | 選填 | 生日 |
| `Patient.identifier[]` | `payload.patient.nationalId`、`payload.patient.nhiCardNo` / `data.patient.identifier[]` | 選填 | 識別碼 |

### 2.2 錯誤碼
- `PATIENT_NOT_FOUND`
- `VALIDATION_ERROR`
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`

## 3. Practitioner

### 3.1 FHIR 欄位與 Facade 欄位
| FHIR 欄位 | Facade payload/response 欄位 | 必填 | 說明 |
| --- | --- | --- | --- |
| `Practitioner.id` | `data.practitioner.id` / `data.items[].id` | 回應必有 | 醫事人員 ID |
| `Practitioner.name[0].family` | `payload.family` / `data.practitioner.name[].family` | `family` 或 `given` 至少一個 | 姓氏 |
| `Practitioner.name[0].given[0]` | `payload.given` / `data.practitioner.name[].given[]` | `family` 或 `given` 至少一個 | 名字 |
| `Practitioner.active` | `payload.active` / `data.practitioner.active` | 選填 | 啟用狀態 |
| `Practitioner.identifier[0].system` | `payload.identifierSystem` / `data.practitioner.identifier[].system` | 與 `identifierValue` 成對 | 識別系統 |
| `Practitioner.identifier[0].value` | `payload.identifierValue` / `data.practitioner.identifier[].value` | 與 `identifierSystem` 成對 | 識別值 |

### 3.2 錯誤碼
- `PRACTITIONER_NOT_FOUND`
- `VALIDATION_ERROR`
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`

## 4. Observation（Phase 1 相容基線）

### 4.1 FHIR 欄位與 Facade 欄位
| FHIR 欄位 | Facade payload/response 欄位 | 必填 | 說明 |
| --- | --- | --- | --- |
| `Observation.id` | `data.observations[].id` | 回應必有 | 觀察資料 ID |
| `Observation.subject.reference` | `Patient/{id}`（path 參數） | 必填 | 關聯病人 |
| `Observation.code` | `payload.biomarker.*` 或 intake 對應欄位 | 依流程 | 觀察代碼 |
| `Observation.effectiveDateTime` | `data.observations[].effectiveDateTime` | 建議填 | 生效時間 |
| `Observation.value*` | `payload` 各 intake/biomarker 欄位 | 依代碼 | 觀察值 |

### 4.2 錯誤碼
- `OBSERVATION_NOT_FOUND`
- `VALIDATION_ERROR`
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`

## 5. Condition（Phase 2/3 重點）

### 5.1 FHIR 欄位與 Facade 欄位
| FHIR 欄位 | Facade payload/response 欄位 | 必填 | 說明 |
| --- | --- | --- | --- |
| `Condition.subject.reference` | path `patientId` | 必填 | `Patient/{id}` |
| `Condition.clinicalStatus.coding[0].code` | `payload.clinicalStatus` | 必填 | 允許：`active|recurrence|relapse|inactive|remission|resolved` |
| `Condition.code.text` | `payload.codeText` | `codeText` 或 `code` 至少一個 | 診斷文字 |
| `Condition.code.coding[0].system` | `payload.code.system` | `payload.code` 提供時必填 | 代碼系統 |
| `Condition.code.coding[0].code` | `payload.code.code` | `payload.code` 提供時必填 | 代碼值 |
| `Condition.code.coding[0].display` | `payload.code.display` | 選填 | 代碼顯示 |
| `Condition.onsetDateTime` | `payload.onsetDateTime` | 選填 | 發病時間 |
| `Condition.recordedDate` | `payload.recordedDate` | 選填 | 記錄時間 |
| `Condition.note[].text` | `payload.note` | 選填 | 備註 |
| `Condition.asserter.reference` | `payload.asserterPractitionerId` | 選填 | 指向 `Practitioner/{id}` |

### 5.2 錯誤碼
- `CONDITION_NOT_FOUND`
- `VALIDATION_ERROR`（包含 payload 規則不符）
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`

## 6. DocumentReference

### 6.1 FHIR 欄位與 Facade 欄位
| FHIR 欄位 | Facade payload/response 欄位 | 必填 | 說明 |
| --- | --- | --- | --- |
| `DocumentReference.subject.reference` | path `patientId` | 必填 | `Patient/{id}` |
| `DocumentReference.content[0].attachment.contentType` | `payload.contentType` | 必填 | MIME type |
| `DocumentReference.content[0].attachment.url` | `payload.url` | 必填 | 文件 URL |
| `DocumentReference.content[0].attachment.title` | `payload.title` | 選填 | 文件標題 |
| `DocumentReference.description` | `payload.description` | 選填 | 文件說明 |
| `DocumentReference.date` | `payload.date` | 選填 | 文件日期 |
| `DocumentReference.status` | `payload.status`（預設 `current`） | 選填 | 文件狀態 |

### 6.2 錯誤碼
- `DOCUMENTREFERENCE_NOT_FOUND`
- `VALIDATION_ERROR`
- `BAD_REQUEST`
- `NETWORK_ERROR`
- `TIMEOUT`
- `SERVER_ERROR`

## 7. 欄位變更策略（Frontend 協作）

### 7.1 Additive First
- 既有欄位不改名、不移除。
- 新欄位以「可選填」先上線，前端可漸進採用。

### 7.2 Deprecation Window
- 欄位淘汰採雙軌期（至少一個里程碑）。
- 在文件標註 `deprecated`、替代欄位、預計移除版本。

### 7.3 Version Note
- 每次契約調整必須在變更文件加上版本註記：
  - 日期（YYYY-MM-DD）
  - 變更摘要
  - 相容性影響（向後相容/需前端調整）

### 7.4 錯誤碼穩定性
- 前端應優先依 `error.code` 判斷流程。
- `error.message` 可調整文案，但不作為分支依據。
