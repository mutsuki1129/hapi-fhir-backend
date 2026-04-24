param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$InputFile = ".\fhir-model\examples\patient-intake-input.sample.json",
  [string]$BaseUrl = "",
  [string]$OutFile = "",

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
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

$inputJson = Get-Content -Path $InputFile -Raw | ConvertFrom-Json

if ($null -eq $inputJson.patient) {
  throw "Input JSON must contain 'patient' object."
}

if ([string]::IsNullOrWhiteSpace($inputJson.patient.family) -or [string]::IsNullOrWhiteSpace($inputJson.patient.given)) {
  throw "patient.family and patient.given are required."
}

if ([string]::IsNullOrWhiteSpace($inputJson.patient.id)) {
  $inputJson.patient | Add-Member -MemberType NoteProperty -Name id -Value ("patient-" + (Get-Date -Format "yyyyMMddHHmmss"))
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

function New-ObsString {
  param(
    [string]$Id,
    [string]$PatientId,
    [string]$PerformerReference,
    [string]$Code,
    [string]$Display,
    [string]$Value,
    [string]$CategoryCode = "social-history"
  )

  if ([string]::IsNullOrWhiteSpace($Value)) {
    return $null
  }

  return @{
    resourceType = "Observation"
    id = $Id
    text = @{
      status = "generated"
      div = "<div xmlns='http://www.w3.org/1999/xhtml'>${Display}: $Value</div>"
    }
    meta = @{
      profile = @(
        "https://example.org/fhir/StructureDefinition/patient-intake-observation"
      )
    }
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
          system = "https://example.org/fhir/CodeSystem/patient-intake"
          code = $Code
        }
      )
      text = $Display
    }
    subject = @{
      reference = "Patient/$PatientId"
    }
    performer = @(
      @{
        reference = $PerformerReference
      }
    )
    effectiveDateTime = (Get-Date).ToString("o")
    valueString = $Value
  }
}

function Convert-ToCodeToken {
  param([string]$Text)

  $value = $Text.ToLowerInvariant()
  $value = $value -replace "[^a-z0-9]+", "-"
  $value = $value.Trim("-")
  if ([string]::IsNullOrWhiteSpace($value)) {
    return "custom-attribute"
  }
  return $value
}

$patientId = [string]$inputJson.patient.id
$doctorInput = $inputJson.doctor
$intake = $inputJson.intake
$biomarker = $inputJson.biomarker
$extraAttributes = $inputJson.extraAttributes

$patient = @{
  resourceType = "Patient"
  id = $patientId
  text = @{
    status = "generated"
    div = "<div xmlns='http://www.w3.org/1999/xhtml'>Patient intake record for $([string]$inputJson.patient.family) $([string]$inputJson.patient.given)</div>"
  }
  meta = @{
    profile = @(
      "https://example.org/fhir/StructureDefinition/patient-intake-patient"
    )
  }
  name = @(
    @{
      family = [string]$inputJson.patient.family
      given = @([string]$inputJson.patient.given)
    }
  )
}

if (-not [string]::IsNullOrWhiteSpace($inputJson.patient.gender)) {
  $patient.gender = [string]$inputJson.patient.gender
}
if (-not [string]::IsNullOrWhiteSpace($inputJson.patient.birthDate)) {
  $patient.birthDate = [string]$inputJson.patient.birthDate
}

$patientIdentifiers = @()
if (-not [string]::IsNullOrWhiteSpace($inputJson.patient.nationalId)) {
  $patientIdentifiers += @{
    system = "urn:tw:national-id"
    value = [string]$inputJson.patient.nationalId
  }
}
if (-not [string]::IsNullOrWhiteSpace($inputJson.patient.nhiCardNo)) {
  $patientIdentifiers += @{
    system = "urn:tw:nhi-card"
    value = [string]$inputJson.patient.nhiCardNo
  }
}
if ($patientIdentifiers.Count -gt 0) {
  $patient.identifier = $patientIdentifiers
}

$doctorProvided = $false
if ($null -ne $doctorInput) {
  $doctorProvided = (
    -not [string]::IsNullOrWhiteSpace($doctorInput.id) -or
    -not [string]::IsNullOrWhiteSpace($doctorInput.family) -or
    -not [string]::IsNullOrWhiteSpace($doctorInput.given)
  )
}

$doctor = $null
$careTeam = $null
$observationPerformerRef = "Patient/$patientId"
if ($doctorProvided) {
  $doctorId = [string]$doctorInput.id
  if ([string]::IsNullOrWhiteSpace($doctorId)) {
    $doctorId = "practitioner-$patientId"
  }

  $doctorFamily = [string]$doctorInput.family
  $doctorGiven = [string]$doctorInput.given
  if ([string]::IsNullOrWhiteSpace($doctorFamily)) { $doctorFamily = "Unknown" }
  if ([string]::IsNullOrWhiteSpace($doctorGiven)) { $doctorGiven = "Doctor" }

  $doctor = @{
    resourceType = "Practitioner"
    id = $doctorId
    identifier = @(
      @{
        system = "urn:clinic:doctor-id"
        value = $doctorId
      }
    )
    name = @(
      @{
        family = $doctorFamily
        given = @($doctorGiven)
      }
    )
  }

  $careTeam = @{
    resourceType = "CareTeam"
    id = "careteam-$patientId"
    status = "active"
    subject = @{
      reference = "Patient/$patientId"
    }
    participant = @(
      @{
        member = @{
          reference = "Practitioner/$doctorId"
        }
        role = @(
          @{
            text = "Attending physician"
          }
        )
      }
    )
  }

  $patient.generalPractitioner = @(
    @{
      reference = "Practitioner/$doctorId"
    }
  )
  $observationPerformerRef = "Practitioner/$doctorId"
}

$observations = @()

if ($null -ne $intake) {
  $observations += New-ObsString -Id "obs-$patientId-education" -PatientId $patientId -PerformerReference $observationPerformerRef -Code "education-level" -Display "Education level" -Value ([string]$intake.educationLevel) -CategoryCode "social-history"
  $observations += New-ObsString -Id "obs-$patientId-occupation" -PatientId $patientId -PerformerReference $observationPerformerRef -Code "occupation" -Display "Occupation" -Value ([string]$intake.occupation) -CategoryCode "social-history"
  $observations += New-ObsString -Id "obs-$patientId-hobby" -PatientId $patientId -PerformerReference $observationPerformerRef -Code "hobby-interest" -Display "Hobby and interest" -Value ([string]$intake.hobby) -CategoryCode "social-history"
  $observations += New-ObsString -Id "obs-$patientId-psych" -PatientId $patientId -PerformerReference $observationPerformerRef -Code "psychological-traits" -Display "Psychological traits" -Value ([string]$intake.psychologicalTraits) -CategoryCode "survey"
  $observations += New-ObsString -Id "obs-$patientId-behavior" -PatientId $patientId -PerformerReference $observationPerformerRef -Code "behavior-pattern" -Display "Behavior pattern" -Value ([string]$intake.behaviorPattern) -CategoryCode "survey"

  $income = $intake.monthlyIncome
  $expense = $intake.monthlyExpense
  if ($null -ne $income -or $null -ne $expense) {
    $components = @()
    if ($null -ne $income) {
      $components += @{
        code = @{
          coding = @(
            @{
              system = "https://example.org/fhir/CodeSystem/patient-intake"
              code = "monthly-income"
            }
          )
          text = "Monthly income"
        }
        valueQuantity = @{
          value = [decimal]$income
          unit = "TWD/month"
        }
      }
    }
    if ($null -ne $expense) {
      $components += @{
        code = @{
          coding = @(
            @{
              system = "https://example.org/fhir/CodeSystem/patient-intake"
              code = "monthly-expense"
            }
          )
          text = "Monthly expense"
        }
        valueQuantity = @{
          value = [decimal]$expense
          unit = "TWD/month"
        }
      }
    }

    $observations += @{
      resourceType = "Observation"
      id = "obs-$patientId-finance"
      text = @{
        status = "generated"
        div = "<div xmlns='http://www.w3.org/1999/xhtml'>Financial status observation</div>"
      }
      meta = @{
        profile = @(
          "https://example.org/fhir/StructureDefinition/patient-intake-observation"
        )
      }
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
            system = "https://example.org/fhir/CodeSystem/patient-intake"
            code = "financial-status"
          }
        )
        text = "Income and expense"
      }
      subject = @{
        reference = "Patient/$patientId"
      }
      performer = @(
        @{
          reference = $observationPerformerRef
        }
      )
      effectiveDateTime = (Get-Date).ToString("o")
      component = $components
    }
  }
}

if ($null -ne $biomarker -and $null -ne $biomarker.value -and -not [string]::IsNullOrWhiteSpace($biomarker.code)) {
  $biomarkerDisplay = [string]$biomarker.display
  if ([string]::IsNullOrWhiteSpace($biomarkerDisplay)) {
    $biomarkerDisplay = "Biomarker"
  }
  $biomarkerUnit = [string]$biomarker.unit
  if ([string]::IsNullOrWhiteSpace($biomarkerUnit)) {
    $biomarkerUnit = "1"
  }

  $observations += @{
    resourceType = "Observation"
    id = "obs-$patientId-biomarker-" + (Convert-ToCodeToken -Text ([string]$biomarker.code))
    text = @{
      status = "generated"
      div = "<div xmlns='http://www.w3.org/1999/xhtml'>Biomarker observation: $biomarkerDisplay</div>"
    }
    meta = @{
      profile = @(
        "https://example.org/fhir/StructureDefinition/patient-intake-observation"
      )
    }
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
          system = $(if ([string]::IsNullOrWhiteSpace([string]$biomarker.system)) { "https://example.org/fhir/CodeSystem/biomarker-lite" } else { [string]$biomarker.system })
          code = [string]$biomarker.code
          display = $biomarkerDisplay
        }
      )
      text = $biomarkerDisplay
    }
    subject = @{
      reference = "Patient/$patientId"
    }
    performer = @(
      @{
        reference = $observationPerformerRef
      }
    )
    effectiveDateTime = (Get-Date).ToString("o")
    valueQuantity = @{
      value = [decimal]$biomarker.value
      unit = $biomarkerUnit
    }
  }
}

if ($null -ne $extraAttributes) {
  foreach ($prop in $extraAttributes.PSObject.Properties) {
    $key = [string]$prop.Name
    $rawValue = $prop.Value
    if ($null -eq $rawValue) { continue }

    $valueText = [string]$rawValue
    if ([string]::IsNullOrWhiteSpace($valueText)) { continue }

    $token = Convert-ToCodeToken -Text $key
    $obs = New-ObsString `
      -Id "obs-$patientId-extra-$token" `
      -PatientId $patientId `
      -PerformerReference $observationPerformerRef `
      -Code "extra-custom-attribute" `
      -Display ("Extra attribute: " + $key) `
      -Value $valueText `
      -CategoryCode "survey"
    if ($null -ne $obs) {
      $observations += $obs
    }
  }
}

$entries = @()

$entries += @{
  resource = $patient
  request = @{
    method = "PUT"
    url = "Patient/$patientId"
  }
}

if ($doctorProvided) {
  $entries += @{
    resource = $doctor
    request = @{
      method = "PUT"
      url = "Practitioner/$($doctor.id)"
    }
  }

  $entries += @{
    resource = $careTeam
    request = @{
      method = "PUT"
      url = "CareTeam/$($careTeam.id)"
    }
  }
}

foreach ($obs in $observations) {
  if ($null -eq $obs) { continue }
  $entries += @{
    resource = $obs
    request = @{
      method = "PUT"
      url = "Observation/$($obs.id)"
    }
  }
}

$bundle = @{
  resourceType = "Bundle"
  type = "transaction"
  entry = $entries
}

$requestBody = $bundle | ConvertTo-Json -Depth 80
$response = Invoke-RestMethod -Method Post -Uri "$BaseUrl/fhir" -Headers $headers -Body $requestBody

$summary = [PSCustomObject]@{
  patientId = $patientId
  doctorIncluded = $doctorProvided
  observationCount = ($observations | Where-Object { $null -ne $_ }).Count
  bundleEntryCount = $entries.Count
}

if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
  $response | ConvertTo-Json -Depth 100 | Set-Content -Path $OutFile
  Write-Host "Saved response to $OutFile"
}

$summary | Format-List
