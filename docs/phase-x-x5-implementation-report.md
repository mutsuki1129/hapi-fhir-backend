# Phase X X5 Implementation Report

更新日期：2026-04-29

## 1) 本輪完成摘要

### 1. SMART 細粒度授權模型擴充（主路徑）

已覆蓋 read 主路徑：
- Patient/Observation：`GET /api/patients/{id}/intake-summary`
- Condition：`GET /api/patients/{id}/conditions`、`GET /api/conditions/{id}`
- DocumentReference：`GET /api/patients/{id}/documents`
- Practitioner：`GET /api/practitioners`

scope-to-resource/action（X5）：
- `patient/*.read`
- `patient/Patient.read`
- `patient/Observation.read`
- `patient/Condition.read`
- `patient/DocumentReference.read`
- `user/Practitioner.read`（含 `user/*.read` / `patient/Practitioner.read` 相容）
- `patient/*.write`
- `patient/Media.write`
- `patient/DocumentReference.write`

### 2. deterministic linkage 回應與契約收斂

以 additive 方式在 `source.linkage` 提供可判斷訊號：
- intake-summary：`patient/observation/careTeam/practitioner` explicit/fallback
- conditions list：`condition=explicit`
- condition by id：`model=direct-by-id`
- documents list：`documentReference=explicit`
- media list：`media=explicit`

### 3. Media 二進位上傳正式流程（第一版）

新增 additive 路徑：
- `POST /api/patients/{id}/media/upload`

模式：
- JSON + `payload.contentBase64`
- write scope 檢查
- content-type allowlist + size limit + standardized errors

### 4. Practitioner 契約最終校準（與前端遷移一致）

- `GET /api/practitioners?mode=auth` 已納入 read scope enforcement
- 保持既有回應形狀 `ok/data/error` 不變

### 5. 可封版級回歸矩陣初版（可執行命令）

見下方「回歸矩陣命令」。

## 2) 回歸矩陣命令（初版）

以下命令以 `http://127.0.0.1:8093` 為例：

1. Patient/Observation 401
```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/intake-summary?mode=auth"
```

2. Condition 403（scope 不足）
```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/conditions?mode=auth" `
  -H "Authorization: Bearer test-token" `
  -H "X-SMART-Scopes: patient/Observation.read"
```

3. Condition 200（scope 通過）
```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/conditions?mode=auth&baseUrl=http://localhost:8091" `
  -H "Authorization: Bearer test-token" `
  -H "X-SMART-Scopes: patient/Condition.read"
```

4. DocumentReference 200（scope 通過）
```powershell
curl "http://127.0.0.1:8093/api/patients/patient-001/documents?mode=auth&baseUrl=http://localhost:8091" `
  -H "Authorization: Bearer test-token" `
  -H "X-SMART-Scopes: patient/DocumentReference.read"
```

5. Practitioner 200（scope 通過）
```powershell
curl "http://127.0.0.1:8093/api/practitioners?mode=auth&baseUrl=http://localhost:8091" `
  -H "Authorization: Bearer test-token" `
  -H "X-SMART-Scopes: user/Practitioner.read"
```

6. Media upload 413
```powershell
curl -X POST "http://127.0.0.1:8093/api/patients/patient-001/media/upload" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"contentType\":\"application/pdf\",\"contentBase64\":\"QQ==\",\"sizeBytes\":99999999}}"
```

7. Media upload 415
```powershell
curl -X POST "http://127.0.0.1:8093/api/patients/patient-001/media" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"contentType\":\"application/zip\",\"url\":\"https://example.com/a.zip\",\"sizeBytes\":100}}"
```

## 3) 已知卡點 / 風險 / 最小剩餘工作

### A. auth 真實 token 全覆蓋
- 卡點：目前多數驗證用測試 token + `X-SMART-Scopes` header。
- 風險：真實 IdP claim 結構差異可能影響行為。
- 最小剩餘工作：以真實 Keycloak token 重跑矩陣並留存證據。

### B. deterministic linkage 更強版本
- 卡點：目前為訊號欄位（explicit/fallback），尚未含強一致快照鍵。
- 風險：跨資源 latest 時差仍存在。
- 最小剩餘工作：新增 `fetchedAt/linkageVersion`（additive）並補 smoke。

### C. media 上傳治理
- 卡點：已提供 base64 版正式入口，但尚未接外部 object storage。
- 風險：大檔與掃毒策略仍不足。
- 最小剩餘工作：導入 signed URL / AV 掃描 / multipart streaming guard。
