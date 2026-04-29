# Phase X X4 Backend Upload Contract

更新日期：2026-04-29

## 1) 範圍

X4 第一版採「既有 JSON 模式」補強，不新增破壞性 endpoint。

適用路徑：
- `POST /api/patients/{id}/media`
- `POST /api/patients/{id}/documents`

## 2) Request（JSON）

```json
{
  "mode": "dev",
  "payload": {
    "contentType": "application/pdf",
    "url": "https://example.com/file.pdf",
    "sizeBytes": 1024
  }
}
```

必要欄位：
- `payload.contentType`
- `payload.url`

可選欄位：
- `payload.sizeBytes`
- `payload.contentBase64`（若提供可用於估算大小）
- Media: `title`, `creation`, `note`, `operatorPractitionerId`
- DocumentReference: `title`, `description`, `date`

## 3) 安全限制（X4）

預設允許 content types：
- `image/png`
- `image/jpeg`
- `image/webp`
- `application/pdf`
- `text/plain`

預設大小限制：
- `ATTACHMENT_MAX_BYTES=10485760`（10MB）

可透過環境變數覆寫：
- `ATTACHMENT_ALLOWED_CONTENT_TYPES`
- `ATTACHMENT_MAX_BYTES`

## 4) 錯誤碼與狀態

| HTTP | error.code | 說明 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 缺欄位、型別錯誤、base64 格式錯誤 |
| 413 | `PAYLOAD_TOO_LARGE` | 超過大小限制 |
| 415 | `UNSUPPORTED_MEDIA_TYPE` | contentType 不在允許清單 |
| 500 | `INTERNAL_ERROR` | 未預期錯誤 |

## 5) 回應形狀

成功：

```json
{
  "ok": true,
  "data": {},
  "source": {}
}
```

失敗：

```json
{
  "ok": false,
  "error": {
    "code": "UNSUPPORTED_MEDIA_TYPE",
    "httpStatus": 415
  }
}
```
