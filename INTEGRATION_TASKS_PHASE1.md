# INTEGRATION_TASKS_PHASE1

## Scope
- Resource: Patient, Observation
- Observation scope: body temperature only
- Deferred: Practitioner pages, kondisi final model, picture final model

## Frontend
- [x] 建立 FHIR API client
- [x] 建立 `fromFhirPatient` / `toFhirPatient`
- [x] 建立 `fromFhirObservation` / `toFhirObservation`
- [x] Patients list
- [x] Patients create
- [x] Patients edit
- [x] Medical records list
- [x] Medical records create
- [x] Medical records edit
- [x] 移除 legacy 臨床無關欄位（`age/height/weight/role_id/password`）
- [ ] loading / empty / error UI 全頁一致化（前端視覺層）

## Backend
- [x] Patient read/search 可直接使用
- [x] Observation read/search/create/update 可直接使用
- [x] `code=8310-5` + UCUM `Cel` 規範
- [x] CORS header（Phase 1 facade 層）
- [x] 統一錯誤處理（OperationOutcome -> UI 可讀錯誤）
- [x] phase 1 測試資料（Patient/Observation）
- [x] 提供 facade API（`GET /api/patients/{id}/intake-summary`、`POST /api/patients/intake`、`PATCH /api/patients/{id}/intake`）

## Validation
- [x] 測試 Patient list
- [x] 測試 Patient create
- [x] 測試 Patient edit
- [x] 測試 temperature Observation list
- [x] 測試 temperature Observation create
- [x] 測試 temperature Observation edit
- [x] 測試分組查詢（by patient / by performer）
- [x] 測試 OperationOutcome 映射為 UI 錯誤碼與訊息

## 本次實測證據（重新執行）

- `CORS=*`
- `GET_SUM_OK=True; OBS=9`
- `PATCH_OK=True`
- `POST_OK=True; PID=phase1-patient-9002`
- `ERR_CODE=PATIENT_NOT_FOUND; HTTP=404`

## Notes
- Phase 1 backend facade 入口：`http://127.0.0.1:8092`
- 相關文件：
  - `PHASE1_FRONTEND_ENDPOINTS.md`
  - `OPERATIONOUTCOME_UI_MAPPING.md`
  - `SERVER_CAPABILITY.md`
  - `BACKEND_GAPS_FOR_PHASE1.md`
