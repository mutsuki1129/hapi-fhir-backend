param(
  [string]$CsvFile = ".\fhir-model\examples\patient-intake-batch.sample.csv",
  [string]$OutFile = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $CsvFile)) {
  throw "CSV file not found: $CsvFile"
}

$requiredColumns = @(
  "patient_id", "family", "given", "gender", "birth_date",
  "national_id", "nhi_card_no", "doctor_id", "doctor_family", "doctor_given",
  "education_level", "occupation", "monthly_income", "monthly_expense",
  "hobby", "psychological_traits", "behavior_pattern",
  "biomarker_code", "biomarker_display", "biomarker_value", "biomarker_unit",
  "extra_income_source", "extra_living_status"
)

$rows = Import-Csv -Path $CsvFile
if ($rows.Count -eq 0) {
  throw "CSV has no rows: $CsvFile"
}

$columnNames = @($rows[0].PSObject.Properties.Name)
foreach ($col in $requiredColumns) {
  if ($columnNames -notcontains $col) {
    throw "CSV missing required column: $col"
  }
}

function Add-Issue {
  param(
    [ref]$Issues,
    [int]$RowNumber,
    [string]$PatientId,
    [string]$Field,
    [string]$Severity,
    [string]$Message
  )
  $Issues.Value += [PSCustomObject]@{
    row = $RowNumber
    patient_id = $PatientId
    field = $Field
    severity = $Severity
    message = $Message
  }
}

$issues = @()
$rowNumber = 1

foreach ($row in $rows) {
  $patientId = [string]$row.patient_id
  if ([string]::IsNullOrWhiteSpace($patientId)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "patient_id" -Severity "error" -Message "patient_id is required."
  } elseif ($patientId -notmatch '^[A-Za-z0-9\-.]{3,64}$') {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "patient_id" -Severity "error" -Message "patient_id must be 3-64 chars (letters/numbers/-/.)"
  }

  if ([string]::IsNullOrWhiteSpace([string]$row.family)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "family" -Severity "error" -Message "family is required."
  }
  if ([string]::IsNullOrWhiteSpace([string]$row.given)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "given" -Severity "error" -Message "given is required."
  }

  $gender = [string]$row.gender
  if ($gender -notin @("male", "female", "other", "unknown")) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "gender" -Severity "error" -Message "gender must be one of: male, female, other, unknown."
  }

  $birthDate = [string]$row.birth_date
  if ($birthDate -notmatch '^\d{4}-\d{2}-\d{2}$') {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "birth_date" -Severity "error" -Message "birth_date must be YYYY-MM-DD."
  } else {
    try {
      $dt = [datetime]::ParseExact($birthDate, "yyyy-MM-dd", $null)
      if ($dt -gt (Get-Date)) {
        Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "birth_date" -Severity "error" -Message "birth_date cannot be in the future."
      }
    } catch {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "birth_date" -Severity "error" -Message "birth_date is not a valid calendar date."
    }
  }

  $nationalId = [string]$row.national_id
  if ($nationalId -notmatch "^[A-Z][0-9]{9}$") {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "national_id" -Severity "error" -Message "national_id must match pattern ^[A-Z][0-9]{9}$."
  }

  $nhiCardNo = [string]$row.nhi_card_no
  if ([string]::IsNullOrWhiteSpace($nhiCardNo)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "nhi_card_no" -Severity "error" -Message "nhi_card_no is required."
  }

  if ([string]::IsNullOrWhiteSpace([string]$row.doctor_id)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "doctor_id" -Severity "warning" -Message "doctor_id is empty; importer will generate a fallback ID."
  }

  $monthlyIncome = $null
  if (-not [string]::IsNullOrWhiteSpace([string]$row.monthly_income)) {
    try { $monthlyIncome = [decimal]$row.monthly_income } catch { $monthlyIncome = $null }
    if ($null -eq $monthlyIncome) {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "monthly_income" -Severity "error" -Message "monthly_income must be numeric."
    } elseif ($monthlyIncome -lt 0) {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "monthly_income" -Severity "error" -Message "monthly_income must be >= 0."
    }
  }

  $monthlyExpense = $null
  if (-not [string]::IsNullOrWhiteSpace([string]$row.monthly_expense)) {
    try { $monthlyExpense = [decimal]$row.monthly_expense } catch { $monthlyExpense = $null }
    if ($null -eq $monthlyExpense) {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "monthly_expense" -Severity "error" -Message "monthly_expense must be numeric."
    } elseif ($monthlyExpense -lt 0) {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "monthly_expense" -Severity "error" -Message "monthly_expense must be >= 0."
    }
  }

  if ($null -ne $monthlyIncome -and $null -ne $monthlyExpense -and $monthlyExpense -gt ($monthlyIncome * 2)) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "monthly_expense" -Severity "warning" -Message "monthly_expense is unusually high (>2x monthly_income)."
  }

  $biomarkerCode = [string]$row.biomarker_code
  $biomarkerValueRaw = [string]$row.biomarker_value
  $hasBiomarkerCode = -not [string]::IsNullOrWhiteSpace($biomarkerCode)
  $hasBiomarkerValue = -not [string]::IsNullOrWhiteSpace($biomarkerValueRaw)

  if ($hasBiomarkerCode -xor $hasBiomarkerValue) {
    Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "biomarker" -Severity "error" -Message "biomarker_code and biomarker_value must be provided together."
  }

  if ($hasBiomarkerValue) {
    try {
      $biomarkerValue = [decimal]$biomarkerValueRaw
      if ($biomarkerValue -lt 0) {
        Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "biomarker_value" -Severity "error" -Message "biomarker_value must be >= 0."
      }
    } catch {
      Add-Issue -Issues ([ref]$issues) -RowNumber $rowNumber -PatientId $patientId -Field "biomarker_value" -Severity "error" -Message "biomarker_value must be numeric."
    }
  }

  $rowNumber++
}

$errorCount = @($issues | Where-Object { $_.severity -eq "error" }).Count
$warningCount = @($issues | Where-Object { $_.severity -eq "warning" }).Count

if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
  $issues | Export-Csv -Path $OutFile -NoTypeInformation -Encoding UTF8
  Write-Host "Validation report saved to $OutFile"
}

[PSCustomObject]@{
  rows = $rows.Count
  errors = $errorCount
  warnings = $warningCount
} | Format-List

if ($issues.Count -gt 0) {
  $issues | Format-Table -AutoSize
}
