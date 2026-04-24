param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BaseUrl = "",
  [string]$PatientId = "",
  [string]$NationalId = "",

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

function Get-FirstResourceFromSearchBundle {
  param([object]$Bundle)

  if ($null -eq $Bundle) { return $null }
  if ($Bundle.resourceType -ne "Bundle") { return $null }
  if (-not $Bundle.entry -or $Bundle.entry.Count -eq 0) { return $null }
  return $Bundle.entry[0].resource
}

$patient = $null

if (-not [string]::IsNullOrWhiteSpace($PatientId)) {
  $patient = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Patient/$PatientId" -Headers $headers
} else {
  $patientSearch = Invoke-RestMethod `
    -Method Get `
    -Uri "$BaseUrl/fhir/Patient?identifier=urn:tw:national-id|$([uri]::EscapeDataString($NationalId))" `
    -Headers $headers

  $patient = Get-FirstResourceFromSearchBundle -Bundle $patientSearch
  if ($null -eq $patient) {
    throw "No patient found by National ID: $NationalId"
  }
}

$patientResourceId = $patient.id

$observationBundle = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/fhir/Observation?subject=Patient/$patientResourceId&_count=200" `
  -Headers $headers

$careTeamBundle = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/fhir/CareTeam?subject=Patient/$patientResourceId&_count=50" `
  -Headers $headers

$careTeams = @()
$practitionerRefs = @{}

if ($careTeamBundle.resourceType -eq "Bundle" -and $careTeamBundle.entry) {
  foreach ($entry in $careTeamBundle.entry) {
    $ct = $entry.resource
    $careTeams += $ct
    if ($ct.participant) {
      foreach ($p in $ct.participant) {
        if ($p.member -and $p.member.reference -and $p.member.reference.StartsWith("Practitioner/")) {
          $practitionerRefs[$p.member.reference] = $true
        }
      }
    }
  }
}

if ($patient.generalPractitioner) {
  foreach ($gp in $patient.generalPractitioner) {
    if ($gp.reference -and $gp.reference.StartsWith("Practitioner/")) {
      $practitionerRefs[$gp.reference] = $true
    }
  }
}

$practitioners = @()
foreach ($ref in $practitionerRefs.Keys) {
  $id = $ref.Substring("Practitioner/".Length)
  try {
    $pr = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Practitioner/$id" -Headers $headers
    $practitioners += $pr
  } catch {
    # Skip broken references but continue result aggregation.
  }
}

$observations = @()
if ($observationBundle.resourceType -eq "Bundle" -and $observationBundle.entry) {
  foreach ($entry in $observationBundle.entry) {
    $observations += $entry.resource
  }
}

$result = [PSCustomObject]@{
    patient = $patient
  careTeams = $careTeams
  practitioners = $practitioners
  observations = $observations
  summary = [PSCustomObject]@{
    patientId = $patientResourceId
    careTeamCount = $careTeams.Count
    practitionerCount = $practitioners.Count
    observationCount = $observations.Count
  }
}

if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
  $result | ConvertTo-Json -Depth 100 | Set-Content -Path $OutFile
  Write-Host "Saved to $OutFile"
}

$result.summary | Format-Table -AutoSize
