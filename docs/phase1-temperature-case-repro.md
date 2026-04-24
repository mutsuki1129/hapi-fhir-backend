# Phase 1 Temperature Case Repro

This sample stays in Phase 1 scope and uses only `Patient` + `Observation`.

## Sample file

- `fhir-model/examples/phase1-temperature-case.sample.json`

## Import to dev FHIR

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import-intake-example.ps1 `
  -Mode dev `
  -BundlePath .\fhir-model\examples\phase1-temperature-case.sample.json
```

## Verify

```powershell
curl "http://localhost:8091/fhir/Patient/phase1-patient-temp-001"
curl "http://localhost:8091/fhir/Observation/obs-phase1-patient-temp-001-body-temperature"
```
