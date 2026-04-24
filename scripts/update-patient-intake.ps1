param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BaseUrl = "",
  [string]$PatientId = "",
  [string]$NationalId = "",

  [string]$NameFamily = "",
  [string]$NameGiven = "",
  [ValidateSet("male", "female", "other", "unknown", "")]
  [string]$Gender = "",
  [string]$BirthDate = "",
  [string]$NewNationalId = "",
  [string]$NhiCardNo = "",

  [string]$EducationLevel = "",
  [string]$Occupation = "",
  [Nullable[decimal]]$MonthlyIncome = $null,
  [Nullable[decimal]]$MonthlyExpense = $null,
  [string]$Hobby = "",
  [string]$PsychologicalTraits = "",
  [string]$BehaviorPattern = "",

  [string]$BiomarkerCode = "",
  [string]$BiomarkerDisplay = "",
  [Nullable[decimal]]$BiomarkerValue = $null,
  [string]$BiomarkerUnit = "",

  [string]$DoctorPractitionerId = "",
  [string]$DoctorFamily = "",
  [string]$DoctorGiven = "",

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($PatientId) -and [string]::IsNullOrWhiteSpace($NationalId)) {
  throw "Please provide -PatientId or -NationalId."
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  if ($Mode -eq "auth") {
    $BaseUrl = "http://localhost:8090"
  } else {
    $BaseUrl = "http://localhost:8091"
  }
}

$headers = @{
  "Accept" = "application/fhir+json"
  "Content-Type" = "application/fhir+json"
}

if ($Mode -eq "auth") {
  if ([string]::IsNullOrWhiteSpace($AccessToken)) {
    $tokenResponse = Invoke-RestMethod `
      -Method Post `
      -Uri "$KeycloakUrl/realms/fhir/protocol/openid-connect/token" `
      -ContentType "application/x-www-form-urlencoded" `
      -Body "client_id=$ClientId&client_secret=$ClientSecret&grant_type=password&username=$Username&password=$Password"
    $AccessToken = $tokenResponse.access_token
  }

  if ([string]::IsNullOrWhiteSpace($AccessToken)) {
    throw "Failed to obtain access token."
  }

  $headers["Authorization"] = "Bearer $AccessToken"
}

function Get-FirstBundleResource {
  param([object]$Bundle)
  if ($null -eq $Bundle) { return $null }
  if ($Bundle.resourceType -ne "Bundle") { return $null }
  if (-not $Bundle.entry -or $Bundle.entry.Count -eq 0) { return $null }
  return $Bundle.entry[0].resource
}

function Upsert-ObservationString {
  param(
    [string]$Code,
    [string]$Display,
    [string]$Value,
    [string]$CategoryCode,
    [string]$PatientResourceId
  )

  if ([string]::IsNullOrWhiteSpace($Value)) { return $null }

  $system = "https://example.org/fhir/CodeSystem/patient-intake"
  $searchUrl = "$BaseUrl/fhir/Observation?subject=Patient/$PatientResourceId&code=$([uri]::EscapeDataString("$system|$Code"))&_count=1"
  $bundle = Invoke-RestMethod -Method Get -Uri $searchUrl -Headers $headers
  $obs = Get-FirstBundleResource -Bundle $bundle

  if ($null -eq $obs) {
    $obs = @{
      resourceType = "Observation"
      status = "final"
      category = @(
        @{
          coding = @(
            @{
              system = "http://terminology.hl7.org/CodeSystem/observation-category"
              code = $CategoryCode
            }
          )
        }
      )
      code = @{
        coding = @(
          @{
            system = $system
            code = $Code
          }
        )
        text = $Display
      }
      subject = @{
        reference = "Patient/$PatientResourceId"
      }
      effectiveDateTime = (Get-Date).ToString("o")
      valueString = $Value
    }
    $body = $obs | ConvertTo-Json -Depth 30
    return Invoke-RestMethod -Method Post -Uri "$BaseUrl/fhir/Observation" -Headers $headers -Body $body
  } else {
    $obs.valueString = $Value
    $obs.effectiveDateTime = (Get-Date).ToString("o")
    $body = $obs | ConvertTo-Json -Depth 30
    return Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/Observation/$($obs.id)" -Headers $headers -Body $body
  }
}

# Resolve patient
$patient = $null
if (-not [string]::IsNullOrWhiteSpace($PatientId)) {
  $patient = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Patient/$PatientId" -Headers $headers
} else {
  $patientBundle = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/fhir/Patient?identifier=urn:tw:national-id|$([uri]::EscapeDataString($NationalId))" `
    -Headers $headers
  $patient = Get-FirstBundleResource -Bundle $patientBundle
  if ($null -eq $patient) {
    throw "No patient found by National ID: $NationalId"
  }
}
$patientResourceId = $patient.id

$updated = [ordered]@{
  patientId = $patientResourceId
}

# Update Patient
$patientChanged = $false
if (-not [string]::IsNullOrWhiteSpace($NameFamily) -or -not [string]::IsNullOrWhiteSpace($NameGiven)) {
  if (-not $patient.name -or $patient.name.Count -eq 0) {
    $patient.name = @(@{})
  }
  if (-not [string]::IsNullOrWhiteSpace($NameFamily)) { $patient.name[0].family = $NameFamily }
  if (-not [string]::IsNullOrWhiteSpace($NameGiven)) { $patient.name[0].given = @($NameGiven) }
  $patientChanged = $true
}

if (-not [string]::IsNullOrWhiteSpace($Gender)) {
  $patient.gender = $Gender
  $patientChanged = $true
}
if (-not [string]::IsNullOrWhiteSpace($BirthDate)) {
  $patient.birthDate = $BirthDate
  $patientChanged = $true
}

if (-not [string]::IsNullOrWhiteSpace($NewNationalId)) {
  if (-not $patient.identifier) { $patient.identifier = @() }
  $existing = $null
  foreach ($id in $patient.identifier) {
    if ($id.system -eq "urn:tw:national-id") { $existing = $id; break }
  }
  if ($null -eq $existing) {
    $patient.identifier += @{ system = "urn:tw:national-id"; value = $NewNationalId }
  } else {
    $existing.value = $NewNationalId
  }
  $patientChanged = $true
}

if (-not [string]::IsNullOrWhiteSpace($NhiCardNo)) {
  if (-not $patient.identifier) { $patient.identifier = @() }
  $existing = $null
  foreach ($id in $patient.identifier) {
    if ($id.system -eq "urn:tw:nhi-card") { $existing = $id; break }
  }
  if ($null -eq $existing) {
    $patient.identifier += @{ system = "urn:tw:nhi-card"; value = $NhiCardNo }
  } else {
    $existing.value = $NhiCardNo
  }
  $patientChanged = $true
}

# Doctor upsert and relation
if (
  -not [string]::IsNullOrWhiteSpace($DoctorPractitionerId) -or
  -not [string]::IsNullOrWhiteSpace($DoctorFamily) -or
  -not [string]::IsNullOrWhiteSpace($DoctorGiven)
) {
  if ([string]::IsNullOrWhiteSpace($DoctorPractitionerId)) {
    $DoctorPractitionerId = "practitioner-001"
  }
  $doctor = $null
  try {
    $doctor = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Practitioner/$DoctorPractitionerId" -Headers $headers
  } catch {
    $doctor = @{
      resourceType = "Practitioner"
      id = $DoctorPractitionerId
      identifier = @(
        @{
          system = "urn:clinic:doctor-id"
          value = $DoctorPractitionerId
        }
      )
      name = @(@{})
    }
  }

  if (-not $doctor.name -or $doctor.name.Count -eq 0) {
    $doctor.name = @(@{})
  }
  if (-not [string]::IsNullOrWhiteSpace($DoctorFamily)) { $doctor.name[0].family = $DoctorFamily }
  if (-not [string]::IsNullOrWhiteSpace($DoctorGiven)) { $doctor.name[0].given = @($DoctorGiven) }

  $doctorBody = $doctor | ConvertTo-Json -Depth 30
  $doctorResp = Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/Practitioner/$DoctorPractitionerId" -Headers $headers -Body $doctorBody
  $updated["practitionerId"] = $doctorResp.id

  $patient.generalPractitioner = @(@{ reference = "Practitioner/$DoctorPractitionerId" })
  $patientChanged = $true

  # Upsert CareTeam
  $careTeamBundle = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/CareTeam?subject=Patient/$patientResourceId&_count=1" -Headers $headers
  $careTeam = Get-FirstBundleResource -Bundle $careTeamBundle
  if ($null -eq $careTeam) {
    $careTeam = @{
      resourceType = "CareTeam"
      id = "careteam-$patientResourceId"
      status = "active"
      subject = @{ reference = "Patient/$patientResourceId" }
      participant = @(
        @{
          member = @{ reference = "Practitioner/$DoctorPractitionerId" }
          role = @(@{ text = "Attending physician" })
        }
      )
    }
  } else {
    $careTeam.participant = @(
      @{
        member = @{ reference = "Practitioner/$DoctorPractitionerId" }
        role = @(@{ text = "Attending physician" })
      }
    )
  }
  $ctBody = $careTeam | ConvertTo-Json -Depth 30
  $ctResp = Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/CareTeam/$($careTeam.id)" -Headers $headers -Body $ctBody
  $updated["careTeamId"] = $ctResp.id
}

if ($patientChanged) {
  $patientBody = $patient | ConvertTo-Json -Depth 30
  $patientResp = Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/Patient/$patientResourceId" -Headers $headers -Body $patientBody
  $updated["patientVersion"] = $patientResp.meta.versionId
}

# Social/behavior observations
$obsEducation = Upsert-ObservationString -Code "education-level" -Display "Education level" -Value $EducationLevel -CategoryCode "social-history" -PatientResourceId $patientResourceId
if ($obsEducation) { $updated["educationObservationId"] = $obsEducation.id }

$obsOccupation = Upsert-ObservationString -Code "occupation" -Display "Occupation" -Value $Occupation -CategoryCode "social-history" -PatientResourceId $patientResourceId
if ($obsOccupation) { $updated["occupationObservationId"] = $obsOccupation.id }

$obsHobby = Upsert-ObservationString -Code "hobby-interest" -Display "Hobby and interest" -Value $Hobby -CategoryCode "social-history" -PatientResourceId $patientResourceId
if ($obsHobby) { $updated["hobbyObservationId"] = $obsHobby.id }

$obsPsych = Upsert-ObservationString -Code "psychological-traits" -Display "Psychological traits" -Value $PsychologicalTraits -CategoryCode "survey" -PatientResourceId $patientResourceId
if ($obsPsych) { $updated["psychObservationId"] = $obsPsych.id }

$obsBehavior = Upsert-ObservationString -Code "behavior-pattern" -Display "Behavior pattern" -Value $BehaviorPattern -CategoryCode "survey" -PatientResourceId $patientResourceId
if ($obsBehavior) { $updated["behaviorObservationId"] = $obsBehavior.id }

# Finance observation (component update)
if ($MonthlyIncome -ne $null -or $MonthlyExpense -ne $null) {
  $system = "https://example.org/fhir/CodeSystem/patient-intake"
  $searchUrl = "$BaseUrl/fhir/Observation?subject=Patient/$patientResourceId&code=$([uri]::EscapeDataString("$system|financial-status"))&_count=1"
  $bundle = Invoke-RestMethod -Method Get -Uri $searchUrl -Headers $headers
  $obs = Get-FirstBundleResource -Bundle $bundle

  if ($null -eq $obs) {
    $obs = @{
      resourceType = "Observation"
      status = "final"
      category = @(
        @{
          coding = @(
            @{
              system = "http://terminology.hl7.org/CodeSystem/observation-category"
              code = "social-history"
            }
          )
        }
      )
      code = @{
        coding = @(
          @{
            system = $system
            code = "financial-status"
          }
        )
        text = "Income and expense"
      }
      subject = @{
        reference = "Patient/$patientResourceId"
      }
      effectiveDateTime = (Get-Date).ToString("o")
      component = @()
    }
  }

  if (-not $obs.component) { $obs.component = @() }

  $incomeComp = $null
  $expenseComp = $null
  foreach ($c in $obs.component) {
    if ($c.code.coding[0].code -eq "monthly-income") { $incomeComp = $c }
    if ($c.code.coding[0].code -eq "monthly-expense") { $expenseComp = $c }
  }

  if ($MonthlyIncome -ne $null) {
    if ($null -eq $incomeComp) {
      $incomeComp = @{
        code = @{
          coding = @(@{
            system = $system
            code = "monthly-income"
          })
          text = "Monthly income"
        }
        valueQuantity = @{
          value = [decimal]$MonthlyIncome
          unit = "TWD/month"
        }
      }
      $obs.component += $incomeComp
    } else {
      $incomeComp.valueQuantity = @{
        value = [decimal]$MonthlyIncome
        unit = "TWD/month"
      }
    }
  }

  if ($MonthlyExpense -ne $null) {
    if ($null -eq $expenseComp) {
      $expenseComp = @{
        code = @{
          coding = @(@{
            system = $system
            code = "monthly-expense"
          })
          text = "Monthly expense"
        }
        valueQuantity = @{
          value = [decimal]$MonthlyExpense
          unit = "TWD/month"
        }
      }
      $obs.component += $expenseComp
    } else {
      $expenseComp.valueQuantity = @{
        value = [decimal]$MonthlyExpense
        unit = "TWD/month"
      }
    }
  }

  $obs.effectiveDateTime = (Get-Date).ToString("o")
  $obsBody = $obs | ConvertTo-Json -Depth 30
  if ($obs.id) {
    $obsResp = Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/Observation/$($obs.id)" -Headers $headers -Body $obsBody
  } else {
    $obsResp = Invoke-RestMethod -Method Post -Uri "$BaseUrl/fhir/Observation" -Headers $headers -Body $obsBody
  }
  $updated["financeObservationId"] = $obsResp.id
}

# Biomarker upsert by LOINC code when provided
if ($BiomarkerValue -ne $null) {
  if ([string]::IsNullOrWhiteSpace($BiomarkerCode)) {
    throw "When -BiomarkerValue is provided, please also provide -BiomarkerCode (e.g. 4548-4)."
  }
  if ([string]::IsNullOrWhiteSpace($BiomarkerDisplay)) {
    $BiomarkerDisplay = "Biomarker"
  }
  if ([string]::IsNullOrWhiteSpace($BiomarkerUnit)) {
    $BiomarkerUnit = "1"
  }

  $searchUrl = "$BaseUrl/fhir/Observation?subject=Patient/$patientResourceId&code=$([uri]::EscapeDataString("http://loinc.org|$BiomarkerCode"))&_count=1"
  $bundle = Invoke-RestMethod -Method Get -Uri $searchUrl -Headers $headers
  $obs = Get-FirstBundleResource -Bundle $bundle

  if ($null -eq $obs) {
    $obs = @{
      resourceType = "Observation"
      status = "final"
      category = @(
        @{
          coding = @(
            @{
              system = "http://terminology.hl7.org/CodeSystem/observation-category"
              code = "laboratory"
            }
          )
        }
      )
      code = @{
        coding = @(
          @{
            system = "http://loinc.org"
            code = $BiomarkerCode
            display = $BiomarkerDisplay
          }
        )
        text = $BiomarkerDisplay
      }
      subject = @{
        reference = "Patient/$patientResourceId"
      }
      effectiveDateTime = (Get-Date).ToString("o")
      valueQuantity = @{
        value = [decimal]$BiomarkerValue
        unit = $BiomarkerUnit
      }
    }
    $obsBody = $obs | ConvertTo-Json -Depth 30
    $obsResp = Invoke-RestMethod -Method Post -Uri "$BaseUrl/fhir/Observation" -Headers $headers -Body $obsBody
  } else {
    $obs.valueQuantity = @{
      value = [decimal]$BiomarkerValue
      unit = $BiomarkerUnit
    }
    $obs.effectiveDateTime = (Get-Date).ToString("o")
    $obsBody = $obs | ConvertTo-Json -Depth 30
    $obsResp = Invoke-RestMethod -Method Put -Uri "$BaseUrl/fhir/Observation/$($obs.id)" -Headers $headers -Body $obsBody
  }
  $updated["biomarkerObservationId"] = $obsResp.id
}

[PSCustomObject]$updated | Format-List
