# Phase 3 Error Contract（M2）

本文件定義 Phase 3 後端錯誤分類與回應策略，維持既有 facade 契約：
- 回應包裝固定 `ok/data/error`
- 不破壞既有 Phase 1/2 路徑
- 前端以 `error.code` 作為流程分支主依據

## 1) 統一回應格式

成功：

```json
{
  "ok": true,
  "data": {},
  "source": {
    "mode": "dev",
    "baseUrl": "http://localhost:8091"
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
    "httpStatus": 400,
    "fhirIssueCode": "processing",
    "diagnostics": "payload.code.system is required when payload.code is provided."
  }
}
```

## 2) 錯誤分類（M2 凍結）

### A. Validation 類（400）
- `VALIDATION_ERROR`：payload 結構或欄位值不合規
  - 例：Condition 缺少 `clinicalStatus`
  - 例：`payload.code` 提供時缺 `code.system` 或 `code.code`
- `BAD_REQUEST`：請求格式可解析但不符合服務端需求

### B. Not Found 類（404）
- `PATIENT_NOT_FOUND`
- `OBSERVATION_NOT_FOUND`
- `CONDITION_NOT_FOUND`
- `MEDIA_NOT_FOUND`
- `DOCUMENTREFERENCE_NOT_FOUND`
- `PRACTITIONER_NOT_FOUND`
- `RESOURCE_NOT_FOUND`（無法判定資源類型時）

### C. Conflict 類（409）
- `CONFLICT_ERROR`：資源狀態衝突或商業規則衝突（預留）
- M2 策略：保留錯誤碼與文件規範，不強制所有端點立即回傳 409

### D. Timeout / Network 類
- `TIMEOUT`（504）：FHIR 請求逾時
- `NETWORK_ERROR`（503）：FHIR 服務不可達

## 3) FHIR OperationOutcome 映射策略

1. 優先使用 HTTP status 決定大類。
2. 404 時解析 diagnostics（例如 `HAPI-2001 ... not known`）映射到 `*_NOT_FOUND`。
3. 400 且 `issue.code` 為 `invalid|structure|value|processing` 映射 `VALIDATION_ERROR`。
4. 其餘未覆蓋情境回 `UNKNOWN_ERROR`，但仍維持 `ok:false` 結構。

## 4) 前端協作規則

1. 只用 `error.code` 判斷流程（重試、提示、導頁）。
2. `error.message` 僅作顯示，不做程式分支。
3. `diagnostics` 與 `rawOperationOutcome` 僅供除錯，不保證長期穩定。

## 5) 向後相容策略

1. Additive first：新增欄位不影響既有欄位。
2. Deprecation window：若需淘汰欄位，先文件標註再進入移除期。
3. Version note：每次錯誤契約變更需附日期、摘要與相容性影響。
