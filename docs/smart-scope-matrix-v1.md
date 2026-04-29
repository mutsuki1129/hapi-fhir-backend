# SMART Scope Matrix v1 (X0 Baseline)

目的：提供 Phase X 開工前最小授權基線，先涵蓋 Patient / Observation。

## 1) Scope 命名基準

- `patient/*.read`
- `patient/*.write`
- `patient/Patient.read`
- `patient/Patient.write`
- `patient/Observation.read`
- `patient/Observation.write`

說明：X0 以 SMART on FHIR 常見命名為參考，實際 IdP/Proxy 轉換規則另於實作階段定版。

## 2) Endpoint × Method × Scope

| Endpoint | Method | 目的 | 最小 scope | 備註 |
| --- | --- | --- | --- | --- |
| `/api/patients/{id}/intake-summary` | `GET` | 讀病人摘要（含 Observation） | `patient/Patient.read` + `patient/Observation.read` | 如拆分策略可改為 `patient/*.read` |
| `/api/patients/intake` | `POST` | 建立 intake（Patient + Observation） | `patient/Patient.write` + `patient/Observation.write` | 若僅接受 broad scope，可先用 `patient/*.write` |
| `/api/patients/{id}/intake` | `PATCH` | 更新 intake | `patient/Patient.write` + `patient/Observation.write` | 同上 |
| `/api/patients/{id}/intake` | `DELETE` | 刪除 intake Observation | `patient/Observation.write` | 明確不刪 Patient |
| `/api/process` | `POST` | CSV 匯入流程 | `patient/Patient.write` + `patient/Observation.write` | 建議上線前加額外角色限制 |

## 3) 授權決策原則（X0）

1. Read/Write 分離：讀取與寫入 scope 不混用。
2. 最小權限優先：可用細粒度 scope 時，不回退 broad scope。
3. 明確拒絕：scope 不足回 `403 FORBIDDEN`，未登入或 token 無效回 `401 UNAUTHORIZED`。

## 4) 待後續確認

1. patient-level subject 綁定是否強制（token subject 與 path patientId 關聯）。
2. backend facade 與 auth proxy 的 scope 映射責任分工。
3. 是否追加 `launch/patient` 與 `offline_access` 的 session 策略。
