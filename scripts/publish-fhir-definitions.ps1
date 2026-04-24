param(
  [ValidateSet("dev", "auth")]
  [string]$Mode = "dev",

  [string]$BaseUrl = "",
  [string]$DefinitionsDir = ".\fhir-model\definitions",

  [string]$KeycloakUrl = "http://localhost:8180",
  [string]$ClientId = "fhir-backend",
  [string]$ClientSecret = "fhir-backend-secret",
  [string]$Username = "fhiruser",
  [string]$Password = "fhiruser123",
  [string]$AccessToken = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $DefinitionsDir)) {
  throw "Definitions directory not found: $DefinitionsDir"
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

$files = Get-ChildItem -Path $DefinitionsDir -Filter *.json -File | Sort-Object Name
if ($files.Count -eq 0) {
  throw "No JSON definition files found in $DefinitionsDir"
}

$result = @()
foreach ($file in $files) {
  $resource = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json
  if ([string]::IsNullOrWhiteSpace($resource.resourceType) -or [string]::IsNullOrWhiteSpace($resource.id)) {
    throw "Invalid FHIR resource in $($file.Name): resourceType/id is required."
  }

  $body = Get-Content -Path $file.FullName -Raw
  $uri = "$BaseUrl/fhir/$($resource.resourceType)/$($resource.id)"
  $resp = Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -Body $body

  $result += [PSCustomObject]@{
    file = $file.Name
    resourceType = $resp.resourceType
    id = $resp.id
    versionId = $resp.meta.versionId
    lastUpdated = $resp.meta.lastUpdated
  }
}

$result | Format-Table -AutoSize
