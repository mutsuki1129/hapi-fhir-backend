param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BundlePath = ".\fhir-model\examples\patient-intake-bundle.json",
  [string]$BaseUrl = "",

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BundlePath)) {
  throw "Bundle file not found: $BundlePath"
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  if ($Mode -eq "auth") {
    $BaseUrl = "http://localhost:8090"
  } else {
    $BaseUrl = "http://localhost:8091"
  }
}

$bundle = Get-Content $BundlePath -Raw | ConvertFrom-Json
if ($bundle.resourceType -ne "Bundle") {
  throw "Input file is not a FHIR Bundle."
}
if (-not $bundle.entry -or $bundle.entry.Count -eq 0) {
  throw "Bundle has no entries."
}

$headers = @{
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

# Ensure referential integrity by writing base entities first.
$priority = @{
  "Practitioner" = 10
  "Patient" = 20
  "CareTeam" = 30
  "Observation" = 40
}

$entries = $bundle.entry | Sort-Object {
  $resourceType = $_.resource.resourceType
  if ($priority.ContainsKey($resourceType)) {
    $priority[$resourceType]
  } else {
    999
  }
}

$result = @()
foreach ($entry in $entries) {
  $resource = $entry.resource
  if (-not $resource) { continue }

  $resourceType = $resource.resourceType
  if ([string]::IsNullOrWhiteSpace($resourceType)) {
    throw "Entry missing resourceType."
  }

  $resourceJson = $resource | ConvertTo-Json -Depth 50

  if ([string]::IsNullOrWhiteSpace($resource.id)) {
    $uri = "$BaseUrl/fhir/$resourceType"
    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $resourceJson
  } else {
    $uri = "$BaseUrl/fhir/$resourceType/$($resource.id)"
    $response = Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -Body $resourceJson
  }

  $result += [PSCustomObject]@{
    resourceType = $response.resourceType
    id = $response.id
    versionId = $response.meta.versionId
    lastUpdated = $response.meta.lastUpdated
  }
}

$result | Format-Table -AutoSize
