<#
.SYNOPSIS
    Regenera os ativos locais do perfil GitHub de Lestar Henriques.
#>
[CmdletBinding()]
param(
    [string]$Image = ".\assets\profile.jpg",
    [int]$Cols = 100
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host "`n[1/3] Gerando radar de competências" -ForegroundColor Cyan
python (Join-Path $root 'scripts\radar.py') --data (Join-Path $root 'assets\skills.json') -o (Join-Path $root 'assets\radar')

Write-Host "`n[2/3] Gerando retrato" -ForegroundColor Cyan
python (Join-Path $root 'scripts\dotify.py') $Image -o (Join-Path $root 'assets\portrait') --cols $Cols --equalize --detail 0.5 --color --circle --reveal

Write-Host "`n[3/3] Concluído" -ForegroundColor Green
Write-Host "Abra preview.html para conferir e SETUP.md para publicar no GitHub.`n"
