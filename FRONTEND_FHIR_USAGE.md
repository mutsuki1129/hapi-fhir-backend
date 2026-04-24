# FRONTEND FHIR Usage Audit

## Scope
- Goal: inventory current frontend pages and map required fields to FHIR without force-fitting old DB models.
- Source scanned: `routes/web.php`, `resources/views/admin/**`, `resources/views/layouts/**`, `app/Http/Controllers/{Pasien,Dokter,Rekam}Controller.php`, `app/Models/**`, `database/migrations/**`.
- Priority domain: Patient + Observation (phase 1).

## 1) Major Pages Scanned

| Area | Route | View | Current backend source |
| --- | --- | --- | --- |
| Dashboard | `/dashboard` | `resources/views/dashboard/admin.blade.php` | static Blade content |
| Patients list | `/pasiens` | `resources/views/admin/pasiens.blade.php` | `PasienController@getPasienList` + `Pasien` model |
| Create patient | `/pasiens/create` | `resources/views/admin/createPasien.blade.php` | `PasienController@create` + `createPasien` |
| Edit patient | `/edit-pasien/{id}` | `resources/views/admin/editPasien.blade.php` + admin partials | `PasienController@editPasien` + `updatePasien` + `photoUpload` |
| Doctors list | `/dokters` | `resources/views/admin/dokters.blade.php` | `DokterController@getDokterList` + `Dokter` model |
| Create doctor | `/dokters/create` | `resources/views/admin/createDokter.blade.php` | `DokterController@create` + `createDokter` |
| Edit doctor | `/edit-dokter/{id}` | `resources/views/admin/editDokter.blade.php` + admin partials | `DokterController@editDokter` + `updateDokter` + `photoUpload` |
| Medical records list | `/rekam` | `resources/views/admin/rekam/list.blade.php` | `RekamController@show` (DB join `rekams/pasiens/dokters`) |
| Medical records by patient | `/rekam/pasien` | `resources/views/admin/rekam/pasien.blade.php` | `RekamController@pasien` |
| Medical records by doctor | `/rekam/dokter` | `resources/views/admin/rekam/dokter.blade.php` | `RekamController@dokter` |
| Create medical record | `/rekam/create` | `resources/views/admin/rekam/create.blade.php` | `RekamController@create` + `store` |
| Edit medical record | `/rekam/{id}/edit` | `resources/views/admin/rekam/edit.blade.php` | `RekamController@edit` + `update` |

## 2) Page Field Requirements and FHIR Mapping

### 2.1 Patient pages (`pasiens`)

| UI field | Current model field | FHIR target | Mapping notes |
| --- | --- | --- | --- |
| id | `pasiens.id` | `Patient.id` | Direct ID mapping |
| name | `pasiens.name` | `Patient.name[0].text` (or family/given split) | Direct with transformation if split later |
| email | `pasiens.email` | `Patient.telecom[system=email].value` | Needs telecom array mapping |
| phone number | `pasiens.phone_number` | `Patient.telecom[system=phone].value` | Needs telecom array mapping |
| age | `pasiens.age` | `Patient.birthDate` (derived age) | Old age integer should be removed; derive in UI |
| height | `pasiens.height` | `Observation(code=8302-2)` | Not Patient core field |
| weight | `pasiens.weight` | `Observation(code=29463-7)` | Not Patient core field |
| profile picture | `pasiens.profile_picture` | `Patient.photo[0].url` | Can map to photo URL if backend supports it |
| role id | `pasiens.role_id` | N/A (app auth concept) | Keep outside FHIR clinical resources |
| password | `pasiens.password` | N/A | Must stay in auth boundary, not Patient resource |

### 2.2 Doctor pages (`dokters`)

| UI field | Current model field | FHIR target | Mapping notes |
| --- | --- | --- | --- |
| id | `dokters.id` | `Practitioner.id` | Direct ID mapping |
| name | `dokters.name` | `Practitioner.name[0].text` | Direct |
| email | `dokters.email` | `Practitioner.telecom[system=email].value` | Telecom mapping |
| phone number | `dokters.phone_number` | `Practitioner.telecom[system=phone].value` | Telecom mapping |
| age | `dokters.age` | N/A (or extension) | Not standard Practitioner core field |
| height | `dokters.height` | N/A | Not Practitioner core field |
| weight | `dokters.weight` | N/A | Not Practitioner core field |
| profile picture | `dokters.profile_picture` | `Practitioner.photo[0].url` | Optional |
| role id | `dokters.role_id` | N/A (app auth concept) | Outside FHIR clinical resource |
| password | `dokters.password` | N/A | Auth only |

### 2.3 Medical record pages (`rekam`)

| UI field | Current model/join field | FHIR target | Mapping notes |
| --- | --- | --- | --- |
| record id | `rekams.id` | `Observation.id` | Phase 1 direct mapping for temperature records |
| patient selector | `rekams.pasien` + `pasiens.id` | `Observation.subject.reference = Patient/{id}` | Direct reference mapping |
| doctor selector | `rekams.dokter` + `dokters.id` | `Observation.performer[0].reference = Practitioner/{id}` | Direct reference mapping |
| health condition (`kondisi`) | `rekams.kondisi` | Prefer `Condition` resource (phase 2) | For phase 1, may temporarily map to `Observation.note[].text` |
| body temperature (`suhu`) | `rekams.suhu` | `Observation.valueQuantity` + `code=8310-5` | Phase 1 core field |
| temperature unit | implicit `C` text | `Observation.valueQuantity.unit/system/code` | Use UCUM (`Cel`) |
| prescription image (`picture`) | `rekams.picture` | `Media`, `DocumentReference`, or `Observation.derivedFrom` | Not Observation core numeric field |
| patient display name | `name_pasien` join alias | `Observation.subject.display` or resolved Patient | Derived display only |
| doctor display name | `name_dokter` join alias | `Observation.performer.display` or resolved Practitioner | Derived display only |
| created/updated time | `created_at` / `updated_at` | `Observation.effectiveDateTime` or `issued` | Map carefully by business semantics |

## 3) Old DB / Old Model Dependencies Found

## 3.1 Routing and naming dependency
- Routes are bound to legacy entities and paths: `/pasiens`, `/dokters`, `/rekam`.
- View and controller naming is entity-specific to old schema (`Pasien`, `Dokter`, `Rekam`).

## 3.2 View-level field dependency
- UI assumes non-FHIR core fields on patient/doctor (`age`, `height`, `weight`, `role_id`).
- UI assumes local filesystem image paths and `storage/` checks (`file_exists(public_path('storage/...'))`).
- Medical records cards rely on SQL join aliases (`name_pasien`, `name_dokter`) from local tables.

## 3.3 Controller-level dependency
- All major pages use Eloquent models tied to local tables (`pasiens`, `dokters`, `rekams`).
- `RekamController` uses DB joins directly against local schema, not resource-driven retrieval.
- Search/sort logic is hardcoded to local column names.

## 3.4 Schema/model inconsistency risk
- `rekams` migration defines `pasien`, `dokter`, `suhu` as string, but controller validates integer references and numeric temperature.
- `Pasien`/`Dokter` models set `$incrementing = false` and `$keyType = 'string'` despite integer `id` migration.
- This confirms tight coupling and drift in legacy data model assumptions.

## 3.5 Test script dependency
- E2E scripts use legacy URLs and form payload fields (`pasien`, `dokter`, `kondisi`, `suhu`, `picture`) tied to old app contracts.

## 4) Page Readiness Classification

| Page group | Classification | Why |
| --- | --- | --- |
| Patients list/create/edit | Needs field adjustment | Can map to `Patient` for name/telecom/photo, but must remove or relocate age/height/weight/role/password assumptions |
| Medical records list/create/edit | Needs field adjustment (phase 1 subset) | Temperature fits `Observation`; condition text and prescription image do not cleanly fit phase 1 |
| Medical records grouped views | Needs adjustment | Grouping can be recreated from Observation by subject/performer, but current implementation depends on SQL aliases |
| Doctors list/create/edit | Redesign or defer | Backend-first scope is Patient + Observation; doctor pages require Practitioner API and contract not in phase 1 |
| Dashboard | Redesign later | Static/garbled content, not resource-driven |
| Auth/Profile | Can stay separate | App-auth concern, should not be merged into FHIR clinical resource payloads |

## 5) Practical Mapping Recommendation (Backend-first)

- Do not treat old `pasiens/dokters/rekams` tables as canonical integration contracts.
- Introduce frontend resource adapters:
  - `PatientViewModel <-> FHIR Patient`
  - `ObservationViewModel <-> FHIR Observation` (temperature only in phase 1)
- Keep legacy-only fields out of phase 1 clinical payloads.

## 6) Immediate Notes for Phase 1 (Patient + Observation)

- In patient screens, keep only fields that map cleanly to Patient now: `name`, `email`, `phone` (and optional `photo`).
- In medical record screens, scope phase 1 to temperature Observation:
  - subject (Patient reference)
  - performer (Practitioner reference, if available)
  - code fixed to body temperature (LOINC 8310-5)
  - valueQuantity (numeric + UCUM Cel)
  - effectiveDateTime
- Move `kondisi` and `picture` to phase 2 design (`Condition` + `Media/DocumentReference`) instead of force mapping.

## 7) Output of This Audit
- This file: `FRONTEND_FHIR_USAGE.md`
- Phase 1 execution plan: `FRONTEND_PHASE1_PLAN.md`