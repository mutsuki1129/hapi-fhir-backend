# Phase X Scope Matrix v2

更新日期：2026-04-29

在 X1 基礎上，擴充 Condition read 策略。

## 1) Scope 集合（v2）

- `patient/*.read`
- `patient/*.write`
- `patient/Patient.read`
- `patient/Observation.read`
- `patient/Condition.read`

## 2) Endpoint × Method × Scope（v2）

| Endpoint | Method | 最小 scope | 備註 |
| --- | --- | --- | --- |
| `/api/patients/{id}/intake-summary` | GET | `patient/*.read` 或 (`patient/Patient.read` + `patient/Observation.read`) | X1 已落地最小 enforcement |
| `/api/patients/{id}/conditions` | GET | `patient/*.read` 或 `patient/Condition.read` | X2 文件策略擴充 |
| `/api/conditions/{id}` | GET | `patient/*.read` 或 `patient/Condition.read` | X2 文件策略擴充 |
| `/api/patients/intake` | POST | `patient/*.write` | 既有策略 |
| `/api/patients/{id}/intake` | PATCH | `patient/*.write` | 既有策略 |
| `/api/patients/{id}/intake` | DELETE | `patient/*.write` 或 `patient/Observation.write` | 既有策略 |

## 3) 401 / 403 判定

1. 無 token 或 token 無法解析：`401 UNAUTHORIZED`
2. 有 token 但 scope 不足：`403 FORBIDDEN`
3. scope 通過但上游授權失敗：保留上游 `401/403`

## 4) 導入建議

### X2（本輪）
- 完成 scope 策略文件與測試計畫更新，不做大改。

### X3（候選）
- 對 Condition GET 路徑補最小 enforcement 掛點（沿用 X1 模式）。

### X4（候選）
- 擴到 DocumentReference/Media/Practitioner 讀取路徑。

## 5) 驗證要點

1. 至少保有一組 `401/403/200` 可重現證據。
2. `requiredScopes` 在 `403` 時可回應（便於前端除錯）。
3. 不破壞 `ok/data/error` 包裝。
