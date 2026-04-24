# FHIR Server 專案完整說明

## 1. 專案定位

本專案是一個以 HAPI FHIR 為核心的本機可執行 FHIR Server 範本，目標是快速提供：
- 可運行的 FHIR API（R4）
- 可切換的開發模式與授權模式
- OAuth2 / OIDC 驗證整合能力
- 後續擴充為正式環境的技術基礎

## 2. 技術棧

- 後端 FHIR 引擎：HAPI FHIR JPA Server（Docker Image）
- 資料庫：PostgreSQL 16
- 身分提供者：Keycloak 26.1.5
- API 授權閘道：OAuth2 Proxy 7.8.1
- 容器編排：Docker Compose
- 腳本：PowerShell（Windows 開發環境）

## 3. 核心功能

- 提供標準 FHIR REST API（如 `Patient` CRUD）
- 提供 metadata 與健康檢查端點
- 支援 `dev` 與 `dev,auth` 運作模式
- 支援 JWT Bearer Token 驗證（auth 模式）
- 提供本機可用的 Keycloak realm、client、測試帳號
- 提供可重現、可移植的容器化部署方式

## 4. 架構與元件關係

- `hapi`：主要 FHIR Server，負責 FHIR 請求處理與資料存取
- `db`：PostgreSQL，儲存 FHIR 資源與索引
- `keycloak`：簽發 OIDC/JWT token，提供身份與權限基礎
- `fhir-proxy`：在 auth 模式下作為唯一公開 FHIR 入口，驗證 token 後轉發至 HAPI

資料流（auth 模式）：
- Client 向 Keycloak 取得 access token
- Client 帶 Bearer Token 呼叫 `http://localhost:8090/fhir/...`
- OAuth2 Proxy 驗證 token
- 驗證通過後，proxy 轉發請求到 `hapi:8090`

## 5. 運作模式

### 5.1 開發模式（dev）

- Compose 檔：`docker-compose.yml` + `docker-compose.dev.yml`
- 對外 port：
- `8091`：HAPI FHIR 直連
- `5432`：PostgreSQL
- 特性：
- 便於快速開發、除錯、資料庫連線
- 不強制 OAuth2 保護

### 5.2 授權模式（auth）

- Compose 檔：`docker-compose.yml` + `docker-compose.auth.yml`
- 對外 port：
- `8090`：受保護 FHIR 入口（OAuth2 Proxy）
- `8180`：Keycloak
- 內網 only（不對 host 暴露）：
- HAPI (`8091` 不可直連)
- PostgreSQL (`5432` 不可直連)
- 特性：
- 強制走 JWT 驗證入口
- 有效避免繞過 proxy 直接打 HAPI/DB

## 6. 安全設計重點

- 透過 OAuth2 Proxy 作為 API Gate，統一驗證策略
- auth 模式下關閉 HAPI/DB host 對外映射，降低繞過風險
- 使用 Keycloak Realm 管理 client 與使用者
- JWT issuer 與 audience 參數已對齊本專案設定

## 7. 專案目錄說明

- `docker-compose.yml`：基礎服務定義（hapi/db/keycloak/proxy）
- `docker-compose.dev.yml`：開發模式覆蓋（開啟 `8091`、`5432`）
- `docker-compose.auth.yml`：授權模式覆蓋（關閉 HAPI host port）
- `config/`：HAPI Spring 設定（base/dev/staging/prod/auth）
- `keycloak/realm/fhir-realm.json`：Keycloak realm 匯入內容
- `scripts/start-dev.ps1`：啟動開發模式
- `scripts/start-dev-auth.ps1`：啟動授權模式
- `README.md`：快速操作手冊（中文）

## 8. 功能現況與限制

已完成：
- FHIR Server 啟動與基本資源操作
- Keycloak token 發放
- auth 模式 401/200 驗證流程
- auth 模式下防繞過（HAPI/DB host port 關閉）

目前限制：
- 使用的是官方 HAPI image，未進行程式碼級客製授權規則
- 權限控管目前以「是否有有效 token」為主，尚未細分 resource/scope 級授權
- Keycloak 目前為開發友善預設值，尚未進行正式環境硬化

## 9. 建議的下一步

- 建立自定 HAPI 應用層，加入細粒度授權（依資源、操作、角色）
- 導入 migration 工具（如 Flyway）與環境化部署流程（dev/staging/prod）
- 導入 API 自動化測試與 CI（含 auth flow）
- 規劃 SMART on FHIR 權限模型與 scope 對應策略
- 強化 Keycloak 與密鑰管理（祕密值、憑證、輪替策略）

## 10. 驗證清單（快速）

- 開發模式：
- `http://localhost:8091/fhir/metadata` 應回應成功

- 授權模式：
- `http://localhost:8090/fhir/Patient` 無 token 應為 401
- 同端點帶 token 應為 200
- `http://localhost:8091/...` 應不可達
- `localhost:5432` 應不可連線
