$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $ScriptDir
$Router = Join-Path $SkillRoot 'config\model-router.toml'
$Template = Join-Path $SkillRoot 'templates\project-context.md'

# Explicit UTF-8 is required for Windows PowerShell 5.1. It otherwise treats
# UTF-8 without BOM as the active ANSI code page when Get-Content is used.
$Utf8Strict = [System.Text.UTF8Encoding]::new($false, $true)

function Read-Utf8Text([string]$Path) {
  return [System.IO.File]::ReadAllText($Path, $Utf8Strict)
}

function Read-Utf8Lines([string]$Path) {
  return [System.IO.File]::ReadAllLines($Path, $Utf8Strict)
}

function Write-Utf8Text([string]$Path, [string]$Text) {
  [System.IO.File]::WriteAllText($Path, $Text, $Utf8Strict)
}

function Read-RouterValue([string]$Section, [string]$Key) {
  $lines = Read-Utf8Lines $Router
  $inSection = $false
  foreach ($raw in $lines) {
    $line = $raw.Trim()
    if ($line -match '^\[(.+)\]$') { $inSection = ($Matches[1] -eq $Section); continue }
    if (-not $inSection) { continue }
    $clean = ($line -replace '#.*$','').Trim()
    if ($clean -match ('^' + [regex]::Escape($Key) + '\s*=\s*"(.*)"\s*$')) { return $Matches[1] }
  }
  return $null
}

function Test-SafeRelativePath([string]$PathValue) {
  if ([string]::IsNullOrWhiteSpace($PathValue)) { return $false }
  if ([IO.Path]::IsPathRooted($PathValue) -or $PathValue.StartsWith('~')) { return $false }
  $parts = $PathValue -split '[\\/]'
  if ($parts -contains '..') { return $false }
  if ($PathValue.Contains("`n") -or $PathValue.Contains("`r")) { return $false }
  return $true
}

$projectRoot = $null
try {
  $candidate = (& git rev-parse --show-toplevel 2>$null | Select-Object -First 1)
  if ($LASTEXITCODE -eq 0 -and $candidate) { $projectRoot = $candidate.Trim() }
} catch {}
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }

$ctxRel = Read-RouterValue 'project_context' 'path'
if (-not $ctxRel) { $ctxRel = '.polyforge/project-context.md' }
if (-not (Test-SafeRelativePath $ctxRel)) { throw "project_context.path must be a safe path inside the project: $ctxRel" }

$legacyRel = Read-RouterValue 'project_context' 'legacy_path'
if ($legacyRel -and -not (Test-SafeRelativePath $legacyRel)) { $legacyRel = $null }

$ctxNative = $ctxRel -replace '/', [IO.Path]::DirectorySeparatorChar
$ctx = Join-Path $projectRoot $ctxNative
$parent = Split-Path -Parent $ctx
New-Item -ItemType Directory -Force -Path $parent | Out-Null

$migrate = Read-RouterValue 'project_context' 'auto_migrate_legacy'
if (-not (Test-Path -LiteralPath $ctx) -and $migrate -eq 'true' -and $legacyRel) {
  $legacy = Join-Path $projectRoot ($legacyRel -replace '/', [IO.Path]::DirectorySeparatorChar)
  if (Test-Path -LiteralPath $legacy) {
    # Validate before copying/re-writing. Invalid source encoding must fail
    # visibly rather than being silently turned into mojibake.
    $legacyText = Read-Utf8Text $legacy
    $legacyLines = $legacyText -split '\r?\n'
    if ($legacyLines.Count -gt 0) { $legacyLines[0] = '# PolyForge Project Context' }
    $joined = $legacyLines -join [Environment]::NewLine
    $text = $joined.TrimEnd([char[]]"`r`n") + [Environment]::NewLine
    Write-Utf8Text $ctx $text
    Write-Host "migrated: $legacyRel -> $ctxRel"
  }
}

if (-not (Test-Path -LiteralPath $ctx)) {
  $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ssK'
  $text = Read-Utf8Text $Template
  $text = $text.Replace('{{TIMESTAMP}}', $ts).Replace('{{PROJECT_ROOT}}', $projectRoot)
  Write-Utf8Text $ctx $text
  Write-Host "created: $ctx"
} else {
  # Fail fast if an existing context file is no longer valid UTF-8.
  $null = Read-Utf8Text $ctx
  Write-Host "exists: $ctx"
}

$exclude = Read-RouterValue 'project_context' 'exclude_from_git'
if ($exclude -eq 'true') {
  try {
    & git -C $projectRoot rev-parse --git-dir *> $null
    if ($LASTEXITCODE -eq 0) {
      $excludeFile = (& git -C $projectRoot rev-parse --git-path info/exclude | Select-Object -First 1).Trim()
      if (-not [IO.Path]::IsPathRooted($excludeFile)) { $excludeFile = Join-Path $projectRoot $excludeFile }
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $excludeFile) | Out-Null
      if (-not (Test-Path -LiteralPath $excludeFile)) { Write-Utf8Text $excludeFile '' }
      $pattern = '/' + ($ctxRel -replace '\\','/')
      $lines = Read-Utf8Lines $excludeFile
      if ($lines -notcontains $pattern) {
        $existing = Read-Utf8Text $excludeFile
        if ($existing.Length -gt 0 -and -not ($existing.EndsWith("`n") -or $existing.EndsWith("`r"))) {
          $existing += [Environment]::NewLine
        }
        $existing += $pattern + [Environment]::NewLine
        Write-Utf8Text $excludeFile $existing
        Write-Host "git-local-exclude: $pattern"
      }
    }
  } catch {
    Write-Warning "Could not update .git/info/exclude safely: $($_.Exception.Message)"
  }
}

Write-Output $ctx
