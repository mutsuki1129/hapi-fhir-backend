# Contract Versioning Policy (X0 Baseline)

目的：規範 facade 契約演進，降低前後端協作風險。

## 1) Additive First

1. 既有欄位不改名、不刪除。
2. 新欄位先以可選填加入。
3. 回應新增欄位不得破壞既有解析流程。

## 2) Deprecation Window

1. 欄位淘汰前需先標記 `deprecated`（文件層）。
2. 至少保留一個里程碑過渡期。
3. 文件需明確標示替代欄位與預計移除時間。

## 3) Version Note（每次必填）

每次契約變更需更新版本說明，至少包含：
1. 日期（YYYY-MM-DD）
2. 變更摘要
3. 相容性影響（向後相容/需調整）
4. 影響端點與欄位

## 4) 錯誤契約穩定性

1. 前端流程分支以 `error.code` 為主。
2. `error.message` 可優化文案，但不作分支依據。
3. 新增錯誤碼需先補文件，再落實程式。

## 5) 變更分級建議

- Patch：文件補充、非破壞欄位新增
- Minor：新 endpoint 或可選行為
- Major：破壞相容變更（X0 禁止）
