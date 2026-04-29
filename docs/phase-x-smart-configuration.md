# Phase X SMART Configuration (X1)

## 1) Endpoint

- `GET /.well-known/smart-configuration`

由 facade 提供，可用環境變數覆寫主要欄位。

## 2) 可設定欄位

- `SMART_ISSUER`
- `SMART_AUTHORIZATION_ENDPOINT`
- `SMART_TOKEN_ENDPOINT`
- `SMART_REGISTRATION_ENDPOINT`
- `SMART_INTROSPECTION_ENDPOINT`
- `SMART_SCOPES_SUPPORTED`（逗號分隔）
- `SMART_CAPABILITIES`（逗號分隔）

## 3) 預設值（X1）

- issuer: `http://localhost:8080/realms/fhir`
- scopes（預設）：
  - `openid`
  - `profile`
  - `launch/patient`
  - `patient/*.read`
  - `patient/*.write`
  - `patient/Patient.read`
  - `patient/Observation.read`

## 4) 驗證命令

```powershell
curl http://127.0.0.1:8093/.well-known/smart-configuration
```

## 5) 限制

X1 僅提供設定端點與最小 scope baseline，不包含完整動態 client registration 流程。
