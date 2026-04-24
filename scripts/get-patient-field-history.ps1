param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BaseUrl = "",
  [string]$PatientId = "",
  [string]$NationalId = "",

  [ValidateSet("all", "name", "gender", "birthDate", "nationalId", "nhiCard", "education", "occupation", "hobby", "psychological", "behavior", "finance", "biomarker")]
  [string]$Field = "all",

  [string]$BiomarkerCode = "4548-4",
  [string]$From = "",
  [string]$To = "",
  [int]$Latest = 0,
  [ValidateSet("asc", "desc")]
  [string]$Order = "asc",
  [switch]$IncludeDeleted,
  [ValidateSet("json", "csv")]
  [string]$OutFormat = "json",
  [ValidateSet("en", "zh-tw")]
  [string]$CsvHeader = "en",
  [string]$OutFile = "",

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

function To-DateTimeOffsetOrNull {
  param([object]$Value)
  if ($null -eq $Value) { return $null }
  try {
    return [DateTimeOffset]::Parse($Value.ToString())
  } catch {
    return $null
  }
}

function Get-BundleEntries {
  param([object]$Bundle)
  if ($null -eq $Bundle) { return @() }
  if ($Bundle.resourceType -ne "Bundle") { return @() }
  if (-not $Bundle.entry) { return @() }
  return $Bundle.entry
}

function Get-FirstBundleResource {
  param([object]$Bundle)
  $entries = Get-BundleEntries -Bundle $Bundle
  if ($entries.Count -eq 0) { return $null }
  return $entries[0].resource
}

function Is-DeletedHistoryEntry {
  param([object]$Entry)
  if ($null -eq $Entry) { return $false }
  if ($Entry.request -and $Entry.request.method -eq "DELETE") { return $true }
  if ($Entry.response -and $Entry.response.status -and $Entry.response.status.ToString().StartsWith("410")) { return $true }
  return $false
}

function Get-IdentifierValue {
  param([object]$Patient, [string]$System)
  if (-not $Patient -or -not $Patient.identifier) { return $null }
  foreach ($id in $Patient.identifier) {
    if ($id.system -eq $System) { return $id.value }
  }
  return $null
}

function Find-ObservationByCode {
  param([string]$PatientResourceId, [string]$CodeSystem, [string]$Code)
  $url = "$BaseUrl/fhir/Observation?subject=Patient/$PatientResourceId&code=$([uri]::EscapeDataString("$CodeSystem|$Code"))&_count=1"
  $bundle = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
  return Get-FirstBundleResource -Bundle $bundle
}

function Build-ObservationHistoryRows {
  param(
    [object]$Observation,
    [string]$FieldName
  )

  $result = @()
  if ($null -eq $Observation) { return $result }

  $historyBundle = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Observation/$($Observation.id)/_history?_count=200" -Headers $headers
  foreach ($entry in (Get-BundleEntries -Bundle $historyBundle)) {
    $isDeleted = Is-DeletedHistoryEntry -Entry $entry
    if ($isDeleted -and -not $IncludeDeleted.IsPresent) { continue }

    $res = $entry.resource
    $meta = if ($res) { $res.meta } else { $null }
    $rid = if ($res) { $res.id } else { $Observation.id }
    $value = $null

    if ($isDeleted) {
      $value = "[deleted]"
    } elseif ($res) {
      switch ($FieldName) {
        "education" {
          if ($res.valueCodeableConcept) {
            if ($res.valueCodeableConcept.text) {
              $value = $res.valueCodeableConcept.text
            } elseif ($res.valueCodeableConcept.coding -and $res.valueCodeableConcept.coding.Count -gt 0) {
              $value = $res.valueCodeableConcept.coding[0].code
            }
          }
        }
        "occupation" { $value = $res.valueString }
        "hobby" { $value = $res.valueString }
        "psychological" { $value = $res.valueString }
        "behavior" { $value = $res.valueString }
        "biomarker" {
          if ($res.valueQuantity) {
            $value = "$($res.valueQuantity.value) $($res.valueQuantity.unit)"
          }
        }
        "finance" {
          $income = $null
          $expense = $null
          if ($res.component) {
            foreach ($c in $res.component) {
              if ($c.code -and $c.code.coding -and $c.code.coding.Count -gt 0) {
                $cc = $c.code.coding[0].code
                if ($cc -eq "monthly-income") { $income = $c.valueQuantity.value }
                if ($cc -eq "monthly-expense") { $expense = $c.valueQuantity.value }
              }
            }
          }
          $value = "income=$income, expense=$expense"
        }
      }
    }

    $lastUpdated = if ($meta) { $meta.lastUpdated } else { $null }
    $versionId = if ($meta) { $meta.versionId } else { $null }
    $result += [PSCustomObject]@{
      field = $FieldName
      resourceType = "Observation"
      resourceId = $rid
      versionId = $versionId
      lastUpdated = $lastUpdated
      lastUpdatedAt = (To-DateTimeOffsetOrNull -Value $lastUpdated)
      isDeleted = $isDeleted
      value = $value
    }
  }

  return $result
}

# Resolve patient
$patient = $null
if (-not [string]::IsNullOrWhiteSpace($PatientId)) {
  $patient = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Patient/$PatientId" -Headers $headers
} else {
  $searchBundle = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/fhir/Patient?identifier=urn:tw:national-id|$([uri]::EscapeDataString($NationalId))" `
    -Headers $headers
  $patient = Get-FirstBundleResource -Bundle $searchBundle
  if ($null -eq $patient) {
    throw "No patient found by National ID: $NationalId"
  }
}
$patientResourceId = $patient.id

$rows = @()

# Patient history backed fields
$needPatientHistory = @("all", "name", "gender", "birthDate", "nationalId", "nhiCard") -contains $Field
if ($needPatientHistory) {
  $patientHistoryBundle = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Patient/$patientResourceId/_history?_count=200" -Headers $headers
  foreach ($entry in (Get-BundleEntries -Bundle $patientHistoryBundle)) {
    $isDeleted = Is-DeletedHistoryEntry -Entry $entry
    if ($isDeleted -and -not $IncludeDeleted.IsPresent) { continue }

    $p = $entry.resource
    $meta = if ($p) { $p.meta } else { $null }
    $rid = if ($p) { $p.id } else { $patientResourceId }
    $lastUpdated = if ($meta) { $meta.lastUpdated } else { $null }
    $versionId = if ($meta) { $meta.versionId } else { $null }
    $pairs = @()

    if ($isDeleted) {
      if ($Field -eq "all") {
        foreach ($f in @("name", "gender", "birthDate", "nationalId", "nhiCard")) {
          $pairs += @{ field = $f; value = "[deleted]" }
        }
      } else {
        $pairs += @{ field = $Field; value = "[deleted]" }
      }
    } elseif ($p) {
      if ($Field -eq "all" -or $Field -eq "name") {
        $nameValue = $null
        if ($p.name -and $p.name.Count -gt 0) {
          $family = $p.name[0].family
          $given = if ($p.name[0].given) { ($p.name[0].given -join " ") } else { "" }
          $nameValue = "$family $given".Trim()
        }
        $pairs += @{ field = "name"; value = $nameValue }
      }
      if ($Field -eq "all" -or $Field -eq "gender") {
        $pairs += @{ field = "gender"; value = $p.gender }
      }
      if ($Field -eq "all" -or $Field -eq "birthDate") {
        $pairs += @{ field = "birthDate"; value = $p.birthDate }
      }
      if ($Field -eq "all" -or $Field -eq "nationalId") {
        $pairs += @{ field = "nationalId"; value = (Get-IdentifierValue -Patient $p -System "urn:tw:national-id") }
      }
      if ($Field -eq "all" -or $Field -eq "nhiCard") {
        $pairs += @{ field = "nhiCard"; value = (Get-IdentifierValue -Patient $p -System "urn:tw:nhi-card") }
      }
    }

    foreach ($pair in $pairs) {
      $rows += [PSCustomObject]@{
        field = $pair.field
        resourceType = "Patient"
        resourceId = $rid
        versionId = $versionId
        lastUpdated = $lastUpdated
        lastUpdatedAt = (To-DateTimeOffsetOrNull -Value $lastUpdated)
        isDeleted = $isDeleted
        value = $pair.value
      }
    }
  }
}

# Observation backed fields
$obsFieldMap = @{
  education = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "education-level" }
  occupation = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "occupation" }
  hobby = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "hobby-interest" }
  psychological = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "psychological-traits" }
  behavior = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "behavior-pattern" }
  finance = @{ system = "https://example.org/fhir/CodeSystem/patient-intake"; code = "financial-status" }
}

$wantedObsFields = if ($Field -eq "all") {
  @("education", "occupation", "hobby", "psychological", "behavior", "finance", "biomarker")
} else {
  @($Field)
}

foreach ($f in $wantedObsFields) {
  if ($f -eq "biomarker") {
    $obs = Find-ObservationByCode -PatientResourceId $patientResourceId -CodeSystem "http://loinc.org" -Code $BiomarkerCode
    $rows += Build-ObservationHistoryRows -Observation $obs -FieldName "biomarker"
  } elseif ($obsFieldMap.ContainsKey($f)) {
    $map = $obsFieldMap[$f]
    $obs = Find-ObservationByCode -PatientResourceId $patientResourceId -CodeSystem $map.system -Code $map.code
    $rows += Build-ObservationHistoryRows -Observation $obs -FieldName $f
  }
}

# Time filters
$fromAt = To-DateTimeOffsetOrNull -Value $From
$toAt = To-DateTimeOffsetOrNull -Value $To
if (-not [string]::IsNullOrWhiteSpace($From) -and $null -eq $fromAt) {
  throw "Invalid -From datetime. Example: 2026-04-23T00:00:00+08:00"
}
if (-not [string]::IsNullOrWhiteSpace($To) -and $null -eq $toAt) {
  throw "Invalid -To datetime. Example: 2026-04-24T00:00:00+08:00"
}
if ($fromAt -and $toAt -and $fromAt -gt $toAt) {
  throw "-From must be earlier than or equal to -To."
}
if ($fromAt) { $rows = $rows | Where-Object { $_.lastUpdatedAt -and $_.lastUpdatedAt -ge $fromAt } }
if ($toAt) { $rows = $rows | Where-Object { $_.lastUpdatedAt -and $_.lastUpdatedAt -le $toAt } }

# Ordering
if ($Order -eq "desc") {
  $rows = $rows | Sort-Object field, lastUpdatedAt -Descending
} else {
  $rows = $rows | Sort-Object field, lastUpdatedAt
}

# Latest N per field
if ($Latest -gt 0) {
  $rows = $rows | Group-Object field | ForEach-Object {
    $sorted = if ($Order -eq "desc") {
      $_.Group | Sort-Object lastUpdatedAt -Descending
    } else {
      $_.Group | Sort-Object lastUpdatedAt
    }
    $sorted | Select-Object -First $Latest
  }

  if ($Order -eq "desc") {
    $rows = $rows | Sort-Object field, lastUpdatedAt -Descending
  } else {
    $rows = $rows | Sort-Object field, lastUpdatedAt
  }
}

$rows = $rows | Select-Object field, resourceType, resourceId, versionId, lastUpdated, isDeleted, value

if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
  if ($OutFormat -eq "csv") {
    if ($CsvHeader -eq "zh-tw") {
      $rowsForCsv = foreach ($r in $rows) {
        [PSCustomObject]@{
          '欄位' = $r.field
          '資源類型' = $r.resourceType
          '資源ID' = $r.resourceId
          '版本' = $r.versionId
          '更新時間' = $r.lastUpdated
          '是否刪除' = $r.isDeleted
          '值' = $r.value
        }
      }
      $rowsForCsv | Export-Csv -Path $OutFile -NoTypeInformation -Encoding UTF8
    } else {
      $rows | Export-Csv -Path $OutFile -NoTypeInformation -Encoding UTF8
    }
  } else {
    $rows | ConvertTo-Json -Depth 20 | Set-Content -Path $OutFile
  }
  Write-Host "Saved to $OutFile"
}

if (-not $rows -or $rows.Count -eq 0) {
  Write-Host "No history rows found."
} else {
  $rows | Format-Table -AutoSize
}

