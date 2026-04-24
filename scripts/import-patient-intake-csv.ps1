param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$CsvFile = ".\fhir-model\examples\patient-intake-batch.sample.csv",
  [string]$BaseUrl = "",
  [string]$ValidationReportPath = "",
  [string]$ImportResultCsvPath = "",
  [string]$ImportResultJsonPath = "",
  [switch]$ValidateOnly,
  [switch]$ContinueOnValidationError,

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $CsvFile)) {
  throw "CSV file not found: $CsvFile"
}

$createScript = Join-Path $PSScriptRoot "create-patient-intake.ps1"
if (-not (Test-Path $createScript)) {
  throw "Required script not found: $createScript"
}

$validateScript = Join-Path $PSScriptRoot "validate-patient-intake-csv.ps1"
if (-not (Test-Path $validateScript)) {
  throw "Required script not found: $validateScript"
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  if ($Mode -eq "auth") {
    $BaseUrl = "http://localhost:8090"
  } else {
    $BaseUrl = "http://localhost:8091"
  }
}

if ([string]::IsNullOrWhiteSpace($ValidationReportPath)) {
  $ValidationReportPath = Join-Path $env:TEMP ("patient-intake-validation-" + [guid]::NewGuid().ToString() + ".csv")
}

function Ensure-ParentDirectory {
  param([string]$Path)
  if ([string]::IsNullOrWhiteSpace($Path)) { return }
  $parent = Split-Path -Path $Path -Parent
  if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path $parent)) {
    New-Item -Path $parent -ItemType Directory -Force | Out-Null
  }
}

# Step 1: Pre-validate CSV
$validateArgs = @(
  "-ExecutionPolicy", "Bypass",
  "-File", $validateScript,
  "-CsvFile", $CsvFile,
  "-OutFile", $ValidationReportPath
)
$null = & powershell @validateArgs
if ($LASTEXITCODE -ne 0) {
  throw "CSV validation failed to execute."
}

$issues = @()
if (Test-Path $ValidationReportPath) {
  $issues = Import-Csv -Path $ValidationReportPath
}
$errorRows = @{}
foreach ($issue in $issues) {
  if ($issue.severity -eq "error") {
    $errorRows[[int]$issue.row] = $true
  }
}

$errorCount = @($issues | Where-Object { $_.severity -eq "error" }).Count
$warningCount = @($issues | Where-Object { $_.severity -eq "warning" }).Count

Write-Host "Validation summary: errors=$errorCount warnings=$warningCount report=$ValidationReportPath"

$validationSummary = [PSCustomObject]@{
  errors = $errorCount
  warnings = $warningCount
  report = $ValidationReportPath
}

if ($ValidateOnly) {
  $output = [PSCustomObject]@{
    generatedAt = (Get-Date).ToString("o")
    mode = $Mode
    csvFile = $CsvFile
    baseUrl = $BaseUrl
    validateOnly = $true
    validationSummary = $validationSummary
    importSummary = [PSCustomObject]@{
      totalRows = 0
      success = 0
      skipped = 0
      failed = 0
    }
    results = @()
  }

  if (-not [string]::IsNullOrWhiteSpace($ImportResultCsvPath)) {
    Ensure-ParentDirectory -Path $ImportResultCsvPath
    @() | Export-Csv -Path $ImportResultCsvPath -NoTypeInformation -Encoding UTF8
    Write-Host "Import result CSV saved to $ImportResultCsvPath"
  }
  if (-not [string]::IsNullOrWhiteSpace($ImportResultJsonPath)) {
    Ensure-ParentDirectory -Path $ImportResultJsonPath
    $output | ConvertTo-Json -Depth 20 | Set-Content -Path $ImportResultJsonPath
    Write-Host "Import result JSON saved to $ImportResultJsonPath"
  }

  return
}

if ($errorCount -gt 0 -and -not $ContinueOnValidationError) {
  throw "Validation found $errorCount error(s). Fix CSV or use -ContinueOnValidationError to import valid rows only."
}

# Step 2: Optional auth token
if ($Mode -eq "auth" -and [string]::IsNullOrWhiteSpace($AccessToken)) {
  $tokenResponse = Invoke-RestMethod `
    -Method Post `
    -Uri "$KeycloakUrl/realms/fhir/protocol/openid-connect/token" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "client_id=$ClientId&client_secret=$ClientSecret&grant_type=password&username=$Username&password=$Password"
  $AccessToken = $tokenResponse.access_token
}

# Step 3: Import rows
$rows = Import-Csv -Path $CsvFile
if ($rows.Count -eq 0) {
  throw "CSV has no rows: $CsvFile"
}

$result = @()
$rowNumber = 1
foreach ($row in $rows) {
  if ($errorRows.ContainsKey($rowNumber)) {
    $result += [PSCustomObject]@{
      row = $rowNumber
      patientId = $row.patient_id
      status = "skipped"
      error = "Row has validation error(s)."
    }
    $rowNumber++
    continue
  }

  $monthlyIncome = $null
  if (-not [string]::IsNullOrWhiteSpace($row.monthly_income)) {
    $monthlyIncome = [decimal]$row.monthly_income
  }

  $monthlyExpense = $null
  if (-not [string]::IsNullOrWhiteSpace($row.monthly_expense)) {
    $monthlyExpense = [decimal]$row.monthly_expense
  }

  $biomarkerValue = $null
  if (-not [string]::IsNullOrWhiteSpace($row.biomarker_value)) {
    $biomarkerValue = [decimal]$row.biomarker_value
  }

  $payload = @{
    patient = @{
      id = $row.patient_id
      family = $row.family
      given = $row.given
      gender = $row.gender
      birthDate = $row.birth_date
      nationalId = $row.national_id
      nhiCardNo = $row.nhi_card_no
    }
    doctor = @{
      id = $row.doctor_id
      family = $row.doctor_family
      given = $row.doctor_given
    }
    intake = @{
      educationLevel = $row.education_level
      occupation = $row.occupation
      monthlyIncome = $monthlyIncome
      monthlyExpense = $monthlyExpense
      hobby = $row.hobby
      psychologicalTraits = $row.psychological_traits
      behaviorPattern = $row.behavior_pattern
    }
    biomarker = @{
      code = $row.biomarker_code
      display = $row.biomarker_display
      value = $biomarkerValue
      unit = $row.biomarker_unit
    }
    extraAttributes = @{
      incomeSource = $row.extra_income_source
      livingStatus = $row.extra_living_status
    }
  }

  $tmpInput = Join-Path $env:TEMP ("patient-intake-" + $row.patient_id + "-" + [guid]::NewGuid().ToString() + ".json")
  $payload | ConvertTo-Json -Depth 30 | Set-Content -Path $tmpInput

  try {
    $args = @(
      "-ExecutionPolicy", "Bypass",
      "-File", $createScript,
      "-Mode", $Mode,
      "-InputFile", $tmpInput,
      "-BaseUrl", $BaseUrl
    )
    if ($Mode -eq "auth" -and -not [string]::IsNullOrWhiteSpace($AccessToken)) {
      $args += @("-AccessToken", $AccessToken)
    }

    $null = & powershell @args
    if ($LASTEXITCODE -ne 0) {
      throw "create-patient-intake.ps1 failed with exit code $LASTEXITCODE"
    }

    $result += [PSCustomObject]@{
      row = $rowNumber
      patientId = $row.patient_id
      status = "success"
      error = ""
    }
  } catch {
    $result += [PSCustomObject]@{
      row = $rowNumber
      patientId = $row.patient_id
      status = "failed"
      error = $_.Exception.Message
    }
  } finally {
    Remove-Item -Path $tmpInput -Force -ErrorAction SilentlyContinue
  }

  $rowNumber++
}

$result | Format-Table -AutoSize

$successCount = @($result | Where-Object { $_.status -eq "success" }).Count
$skippedCount = @($result | Where-Object { $_.status -eq "skipped" }).Count
$failedCount = @($result | Where-Object { $_.status -eq "failed" }).Count

$importSummary = [PSCustomObject]@{
  totalRows = $rows.Count
  success = $successCount
  skipped = $skippedCount
  failed = $failedCount
}

$output = [PSCustomObject]@{
  generatedAt = (Get-Date).ToString("o")
  mode = $Mode
  csvFile = $CsvFile
  baseUrl = $BaseUrl
  validateOnly = $false
  validationSummary = $validationSummary
  importSummary = $importSummary
  results = $result
}

if (-not [string]::IsNullOrWhiteSpace($ImportResultCsvPath)) {
  Ensure-ParentDirectory -Path $ImportResultCsvPath
  $result | Export-Csv -Path $ImportResultCsvPath -NoTypeInformation -Encoding UTF8
  Write-Host "Import result CSV saved to $ImportResultCsvPath"
}
if (-not [string]::IsNullOrWhiteSpace($ImportResultJsonPath)) {
  Ensure-ParentDirectory -Path $ImportResultJsonPath
  $output | ConvertTo-Json -Depth 20 | Set-Content -Path $ImportResultJsonPath
  Write-Host "Import result JSON saved to $ImportResultJsonPath"
}
