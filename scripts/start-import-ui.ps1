param(
  [int]$Port = 8092,
  [string]$HostName = "127.0.0.1",
  [string]$CorsOrigin = "*"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Path $PSScriptRoot -Parent
$pyServer = Join-Path $PSScriptRoot "import_ui_server.py"

if (-not (Test-Path $pyServer)) {
  throw "Python server script not found: $pyServer"
}

python $pyServer --host $HostName --port $Port --project-root $projectRoot --cors-origin $CorsOrigin
