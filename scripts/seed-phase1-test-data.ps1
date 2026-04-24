param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",
  [string]$BaseUrl = "",
  [string]$InputFile = ".\fhir-model\examples\phase1-intake-create.sample.json"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $InputFile)) {
  throw "Input file not found: $InputFile"
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  if ($Mode -eq "auth") {
    $BaseUrl = "http://localhost:8090"
  } else {
    $BaseUrl = "http://localhost:8091"
  }
}

powershell -ExecutionPolicy Bypass -File .\scripts\create-patient-intake.ps1 `
  -Mode $Mode `
  -BaseUrl $BaseUrl `
  -InputFile $InputFile

powershell -ExecutionPolicy Bypass -File .\scripts\update-patient-intake.ps1 `
  -Mode $Mode `
  -BaseUrl $BaseUrl `
  -PatientId phase1-patient-001 `
  -MonthlyIncome 90000 `
  -MonthlyExpense 50000 `
  -BehaviorPattern "Late bedtime on weekdays, exercise on weekends"

Write-Host "Seed data ready: phase1-patient-001"
