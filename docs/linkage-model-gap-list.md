# Linkage Model Gap List (X0 Baseline)

目的：盤點「patient-level/latest 推論」與「明確關聯模型」之間差距。

## 1) 現況摘要

目前 facade 多以 patient-level 查詢組裝結果，屬於 latest 可得狀態推論，非交易一致快照。

## 2) 差距列表

| 項目 | 現況 | 目標 | 風險 | 下一步 |
| --- | --- | --- | --- | --- |
| 讀取一致性 | 各資源分別查詢後組裝 | 具一致性標記或快照邊界 | 跨資源時間差 | 增加查詢時間戳與版本欄位 |
| Patient-Observation 關聯 | 以 `subject=Patient/{id}` 為主 | 保持並加上資料新鮮度註記 | 多來源資料混用 | 補 `source`/`fetchedAt` 文件欄位 |
| Patient-Practitioner 關聯 | 由 `generalPractitioner` / 參照鏈推導 | 明確列出主醫師來源優先序 | 關聯不完整時 UI 歧義 | 文件定義 fallback 規則 |
| Not-found 分支 | 依 diagnostics 映射 `*_NOT_FOUND` | 維持並擴充到更多路徑 | 不同環境字串差異 | 建立 regex/分類測試樣本 |
| 授權綁定 | auth 模式可回 401 | 補齊可重現 403 | 權限防線不足證據 | 落地 `rbac-403-test-plan.md` |

## 3) X0 不做事項

1. 不進行關聯模型重構。
2. 不新增破壞式欄位或 endpoint。
3. 不改變既有 `ok/data/error` 外形。

## 4) 驗收建議（X0）

1. 先文件化差距與策略。
2. 逐項制定可測試案例（401/403、not-found、latest 一致性註記）。
3. 在 Phase X 實作輪分批落地，不一次改大面積行為。
