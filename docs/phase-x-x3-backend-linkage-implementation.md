# Phase X X3 Backend Linkage Implementation

更新日期：2026-04-29

## 1) 本輪目標

在不破壞既有契約下，補上：
1. linkage 可判斷訊號（explicit vs fallback）
2. Condition read scope enforcement（401/403/200 可重現）

## 2) 實作變更（Facade）

檔案：`scripts/import_ui_server.py`

### A. linkage 訊號欄位（最小回應形狀）

1. `GET /api/patients/{id}/intake-summary`
   - `source.linkage` 新增：
     - `model: patient-latest`
     - `patient: explicit`
     - `observation: explicit`
     - `careTeam: explicit_or_fallback`
     - `practitioner: explicit_or_fallback`

2. `GET /api/patients/{id}/conditions`
   - `source.linkage` 新增：
     - `model: patient-latest`
     - `condition: explicit`

3. `GET /api/conditions/{id}`
   - `source.linkage` 新增：
     - `model: direct-by-id`
     - `condition: explicit`

### B. Condition read scope enforcement

新增檢查函式：
- `_require_condition_read_scopes()`

授權規則（`mode=auth`）：
- 需具備 `patient/*.read` 或 `patient/Condition.read`
- 缺 token -> `401 UNAUTHORIZED`
- scope 不足 -> `403 FORBIDDEN`（附 `requiredScopes`）

## 3) 相容性說明

1. 既有 endpoint 路徑不變。
2. 原有回應 `ok/data/error` 結構不變。
3. linkage 欄位為 additive 擴充，不影響舊前端解析。

## 4) 驗證摘要

詳見 `docs/phase-x-x1-verification.md` 的 X3 段落與證據：
- Condition read `401/403/200` 已可重現。
- intake summary 回應已含 `source.linkage`。
