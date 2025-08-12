Param(
  [string]$Image = "deinrepo/betriebskosten:latest",
  [string]$Name = "betriebskosten",
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Backup anlegen..."
$inst = Join-Path $env:APPDATA "Betriebskosten\instance"
if (Test-Path $inst) {
  $backup = "$inst.backup_$(Get-Date -Format yyyyMMdd_HHmm)"
  Copy-Item $inst $backup -Recurse
  Write-Host "Backup erstellt unter $backup"
} else {
  New-Item -ItemType Directory -Force -Path $inst | Out-Null
}

Write-Host "[2/5] Neues Image ziehen: $Image"
docker pull $Image

Write-Host "[3/5] Alten Container stoppen/entfernen (falls vorhanden)"
docker stop $Name 2>$null | Out-Null
docker rm $Name 2>$null | Out-Null

Write-Host "[4/5] Container starten..."
docker run -d --name $Name -p $Port:8000 -v "$inst:/app/instance" $Image | Out-Null

Write-Host "[5/5] Fertig. Öffne http://localhost:$Port ..."
Start-Process "http://localhost:$Port"

