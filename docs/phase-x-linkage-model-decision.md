# Phase X Linkage Model Decision

更新日期：2026-04-29

## 1) 決策目標

釐清 Observation / Condition / DocumentReference 的關聯鍵策略，從「patient-latest 推論」逐步走向「可追溯明確關聯」。

## 2) 現況（X1 前）

1. Observation：主要靠 `Observation.subject.reference=Patient/{id}` 查詢。
2. Condition：以 `Condition.subject.reference=Patient/{id}` 為主，若有 `asserter` 才關聯 Practitioner。
3. DocumentReference：以 `DocumentReference.subject.reference=Patient/{id}` 為主。
4. 聚合讀取多為 patient-level latest，非交易快照。

## 3) 目標模型（Phase X）

1. 主關聯鍵（Primary Link）固定為 `subject.reference`。
2. 次關聯鍵（Secondary Link）保留來源與責任者：
   - Observation：可擴充 performer / basedOn（後續）
   - Condition：asserter
   - DocumentReference：author / custodian（後續）
3. 回應層加註可追溯元資訊：
   - `fetchedAt`
   - `source.mode`
   - 必要時 `linkageVersion`

## 4) 遷移步驟（最小）

### Step A（X2 文件定稿）
- 定義主鍵與次鍵語意（本文件）。
- 補 scope matrix v2 與 versioning v2。

### Step B（X3 可控擴充）
- 在不破壞契約前提下，新增可選追蹤欄位（例如 `fetchedAt`）。
- 補 smoke 測試：同病人多資源一致性觀測。

### Step C（X4 收斂）
- 針對高風險查詢補一致性策略（例如快照 token 或 query time）。
- 逐步降低 `latest 推論` 導致的歧義。

## 5) 風險與取捨

1. 保持相容代表短期仍存在 latest 時差風險。
2. 一次性重構關聯模型成本高，故採分期遷移。
3. 需持續對齊前端對「一致性」的預期與顯示策略。
