param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BaseUrl = "",
  [Parameter(Mandatory = $true)]
  [string]$PatientId,

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"

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

function Get-ValidationSummary {
  param(
    [string]$ResourceType,
    [string]$Id,
    [object]$Outcome
  )

  $errorCount = 0
  $warningCount = 0
  if ($Outcome.issue) {
    foreach ($issue in $Outcome.issue) {
      if ($issue.severity -eq "error" -or $issue.severity -eq "fatal") { $errorCount++ }
      if ($issue.severity -eq "warning") { $warningCount++ }
    }
  }

  return [PSCustomObject]@{
    resourceType = $ResourceType
    id = $Id
    result = $(if ($Outcome.issue -and $Outcome.issue.Count -gt 0) { [string]$Outcome.issue[0].severity } else { "unknown" })
    errors = $errorCount
    warnings = $warningCount
  }
}

$patient = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Patient/$PatientId" -Headers $headers
$obsBundle = Invoke-RestMethod -Method Get -Uri "$BaseUrl/fhir/Observation?subject=Patient/$PatientId&_count=200" -Headers $headers

$patientProfile = "https://example.org/fhir/StructureDefinition/patient-intake-patient"
$obsProfile = "https://example.org/fhir/StructureDefinition/patient-intake-observation"

$results = @()

$patientBody = $patient | ConvertTo-Json -Depth 80
$patientOutcome = Invoke-RestMethod `
  -Method Post `
  -Uri "$BaseUrl/fhir/Patient/`$validate?profile=$([uri]::EscapeDataString($patientProfile))" `
  -Headers $headers `
  -Body $patientBody
$results += Get-ValidationSummary -ResourceType "Patient" -Id $PatientId -Outcome $patientOutcome

if ($obsBundle.resourceType -eq "Bundle" -and $obsBundle.entry) {
  foreach ($entry in $obsBundle.entry) {
    $obs = $entry.resource
    $obsBody = $obs | ConvertTo-Json -Depth 80
    $obsOutcome = Invoke-RestMethod `
      -Method Post `
      -Uri "$BaseUrl/fhir/Observation/`$validate?profile=$([uri]::EscapeDataString($obsProfile))" `
      -Headers $headers `
      -Body $obsBody
    $results += Get-ValidationSummary -ResourceType "Observation" -Id $obs.id -Outcome $obsOutcome
  }
}

$results | Format-Table -AutoSize
