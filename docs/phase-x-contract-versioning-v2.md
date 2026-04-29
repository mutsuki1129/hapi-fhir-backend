# Phase X Contract Versioning v2

更新日期：2026-04-29

## 1) Additive-First（強制）

1. 既有欄位不改名、不刪除、不改語意。
2. 新欄位先以 optional 上線，預設值需可回溯。
3. 新增錯誤碼不可取代既有錯誤碼語意，只可擴充。

## 2) Deprecation Window（最小治理）

1. 需淘汰欄位時，先文件標註 `deprecated`。
2. 至少保留一個里程碑（例如 X2->X3）過渡期。
3. 必須提供替代欄位與遷移說明。
4. 過渡期內不可靜默移除回應欄位。

## 3) Version Note（每次變更必填）

每次契約異動必須在文件附：
1. 日期（YYYY-MM-DD）
2. 影響端點與欄位
3. 變更等級（Patch/Minor/Major）
4. 相容性判定（向後相容/需前端調整）
5. 測試證據連結（驗證文件或命令）

## 4) 變更等級定義

- Patch：文件補充、可選欄位新增、非破壞錯誤碼擴充
- Minor：新增 endpoint/新資源流程（不破壞既有）
- Major：破壞既有契約（Phase X 禁止）

## 5) 錯誤契約治理

1. 前端分支以 `error.code` 為主，`message` 僅顯示用途。
2. 新錯誤碼需先出現在文件，再進入程式。
3. 任何 `UNKNOWN_ERROR` 增長需開 issue 追蹤分類缺口。

## 6) 發版前檢查（最小）

1. 文件索引已同步（`DOCUMENT_INDEX.md`）
2. 主要端點仍維持 `ok/data/error`
3. 401/403/200 至少一組可重現證據
