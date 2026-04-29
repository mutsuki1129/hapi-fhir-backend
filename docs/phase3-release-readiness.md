# Phase 3 Release Readiness (M6-M7)

更新日期：2026-04-29

## 1) 範圍

本文件對應 Phase 3：
- M6 回歸驗收（契約一致性 + M5 checklist 驗證）
- M7 封版收斂（狀態盤點、風險與交接）

契約基線：
- `docs/phase3-field-dictionary.md`
- `docs/phase3-error-contract.md`
- `docs/phase3-practitioner-contract.md`
- `docs/phase3-resource-linkage-contract.md`

## 2) 契約一致性檢查結論

- 欄位字典、錯誤契約、Practitioner 契約、關聯契約已建立且互相對齊。
- 既有 facade `ok/data/error` 包裝策略維持不變。
- 目前未發現文件間的 endpoint 路徑衝突。

狀態：**通過（文件層）**

## 3) M5 Smoke Checklist 執行結果（可重現）

執行時間：2026-04-29（Asia/Taipei）  
目標 facade：`http://127.0.0.1:8092`

已執行檢查：
1. `GET /health`
2. `GET /api/practitioners?mode=dev`
3. `POST /api/practitioners`（validation case）
4. `PATCH /api/practitioners/not-exists-001`
5. `POST /api/patients/demo-patient/conditions`（validation case）

結果摘要：
- 全部請求皆失敗，錯誤為「Unable to connect to the remote server」。
- 判定為環境連線阻塞（facade 未啟動或不可達），非契約文件矛盾。

狀態：**阻塞（環境層）**

## 4) M7 封版收斂判定

### 已完成
- Phase 3 契約文件齊備（field/error/linkage/practitioner/m5-checklist/release-readiness）。
- `PHASE3_PLAN.md`、`待辦事項/Phase 3/backend-待辦.md` 已更新至 M6/M7。
- 文件已同步到 `fhir document/backend` 與 `DOCUMENT_INDEX.md`。

### 未完成（Deferred）
- 需在可連線環境重跑 M5 checklist，補上「實際通過」證據。

## 5) 風險與下一步

1. 風險：目前缺少在線環境 smoke pass 紀錄，封版信心受限。  
   下一步：啟動 facade 後重跑 `docs/phase3-m5-smoke-checklist.md`。

2. 風險：Conflict 錯誤仍未逐端點全面落地。  
   下一步：分批盤點可回 409 的業務情境。

3. 風險：Practitioner identifier 驗證仍採寬鬆策略。  
   下一步：與前端確認是否進入 deprecation window 再加嚴。
