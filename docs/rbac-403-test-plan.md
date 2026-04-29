# RBAC 403 Test Plan (X0 Baseline)

目的：提供最小可重現 `403 FORBIDDEN` 測試策略，與 `401` 做清楚區分。

## 1) 測試前提

1. facade 可連線（例：`http://127.0.0.1:8092`）。
2. auth 模式可連線（`mode=auth`）。
3. IdP 可配置至少兩種角色或 scope 組合。

## 2) 測試帳號設計（最小）

| 帳號 | 角色 | scope | 預期 |
| --- | --- | --- | --- |
| `x0-reader` | read-only | `patient/*.read` | 可 GET，不可 POST/PATCH/DELETE |
| `x0-writer` | writer | `patient/*.read patient/*.write` | 可讀可寫 |
| `x0-none` | limited | 無 patient scope | 所有病歷端點應 403（登入有效） |

## 3) 核心案例

### Case A：401（未授權）
- 條件：無 token 或 token 無效
- 請求：`GET /api/practitioners?mode=auth`
- 預期：`401` + `error.code=UNAUTHORIZED`

### Case B：403（已登入但權限不足）
- 條件：使用 `x0-none`（有效 token，無 patient scope）
- 請求：`GET /api/patients/{id}/intake-summary?mode=auth`
- 預期：`403` + `error.code=FORBIDDEN`

### Case C：讀寫分離
- 條件：使用 `x0-reader`
- 請求 1：`GET /api/patients/{id}/intake-summary?mode=auth`（應成功）
- 請求 2：`PATCH /api/patients/{id}/intake`（應 403）

## 4) 驗證輸出格式

每個案例至少記錄：
1. 請求時間
2. 帳號/角色（可匿名化）
3. endpoint/method
4. HTTP status
5. `error.code`
6. 主要證據（response snippet）

## 5) 失敗排查順序

1. 先確認是不是 `401`（token 問題）。
2. 再確認是不是 `403`（scope/role 問題）。
3. 若回 `200` 但預期 `403`，檢查 proxy scope mapping 與 backend 授權開關。
