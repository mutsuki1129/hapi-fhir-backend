# Phase 3 M5 Backend Smoke Checklist

目的：封版前確認 Phase 3 契約一致性，不改壞既有 endpoint。

關聯基線文件：
- `docs/phase3-field-dictionary.md`
- `docs/phase3-error-contract.md`
- `docs/phase3-practitioner-contract.md`

## A. 前置檢查

- [ ] facade 已啟動（預設 `http://127.0.0.1:8092`）
- [ ] dev FHIR 可連線（預設 `http://localhost:8091/fhir`）
- [ ] 以 `mode=dev` 進行 smoke（除非另有指定）

## B. 共用回應外形

- [ ] 成功回應符合：`ok=true` 且有 `data`
- [ ] 失敗回應符合：`ok=false` 且有 `error.code`
- [ ] 錯誤分支不以 `message` 作流程判斷

## C. Condition（field dictionary + error contract）

1. 正常建立（最小合法 payload）

```powershell
curl -X POST "http://127.0.0.1:8092/api/patients/{patientId}/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"clinicalStatus\":\"active\",\"codeText\":\"Hypertension\"}}"
```

- [ ] `ok=true`
- [ ] `data.condition.resourceType=Condition`

2. 驗證錯誤（缺 `clinicalStatus`）

```powershell
curl -X POST "http://127.0.0.1:8092/api/patients/{patientId}/conditions" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"codeText\":\"Hypertension\"}}"
```

- [ ] `ok=false`
- [ ] `error.code=VALIDATION_ERROR`

## D. Practitioner（M4 契約硬化）

1. list

```powershell
curl "http://127.0.0.1:8092/api/practitioners?mode=dev"
```

- [ ] `ok=true`
- [ ] `data.items` 為陣列
- [ ] `data.summary.count` 存在

2. create（最小合法）

```powershell
curl -X POST "http://127.0.0.1:8092/api/practitioners" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"family\":\"Lin\",\"given\":\"Ming\"}}"
```

- [ ] `ok=true`
- [ ] `data.practitioner.resourceType=Practitioner`

3. create 驗證錯誤（family/given 都缺）

```powershell
curl -X POST "http://127.0.0.1:8092/api/practitioners" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"active\":true}}"
```

- [ ] `ok=false`
- [ ] `error.code=VALIDATION_ERROR`

4. edit not-found

```powershell
curl -X PATCH "http://127.0.0.1:8092/api/practitioners/not-exists-001" `
  -H "Content-Type: application/json" `
  -d "{\"mode\":\"dev\",\"payload\":{\"family\":\"Wang\"}}"
```

- [ ] `ok=false`
- [ ] `error.code=PRACTITIONER_NOT_FOUND`（或至少落在 not-found 分類）

## E. Timeout / Network 分類

- [ ] FHIR 無法連線情境可回 `NETWORK_ERROR`
- [ ] 逾時情境可回 `TIMEOUT`

## F. M5 封版判定

- [ ] 三份契約文件描述與行為一致
- [ ] Phase 3 M1-M4 契約路徑皆可用
- [ ] M5 checklist 已執行並留存結果（可附測試日期與環境）
