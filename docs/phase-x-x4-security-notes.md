# Phase X X4 Security Notes

更新日期：2026-04-29

## 1) 已落地最小安全策略

1. Content-Type allowlist 驗證  
   - 非白名單回 `415 UNSUPPORTED_MEDIA_TYPE`

2. Size limit 驗證  
   - 超過 `ATTACHMENT_MAX_BYTES` 回 `413 PAYLOAD_TOO_LARGE`

3. 輸入格式驗證  
   - 必填欄位缺失或格式異常回 `400 VALIDATION_ERROR`

4. 錯誤碼標準化  
   - `400/413/415/500` 與 `error.code` 對應固定

## 2) 本輪非目標

1. 不做檔案實體儲存（仍由 URL/既有資料流承載）
2. 不做病毒掃描
3. 不做 multipart 新管線全面導入

## 3) 已驗證案例（X4）

1. 不允許 contentType（`application/zip`） -> `415`
2. 超過大小限制（`sizeBytes=99999999`） -> `413`
3. 合法 PDF 請求 -> 成功建立 DocumentReference

## 4) 建議後續（X5+）

1. 增加 URL scheme 白名單（https 優先）
2. 對 `contentBase64` 增加更嚴格解碼與 MIME 一致性檢查
3. 若導入 multipart，上傳入口加上 streaming size guard 與檔名清理
