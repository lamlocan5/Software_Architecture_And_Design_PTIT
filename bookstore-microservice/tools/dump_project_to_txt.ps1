param(
  [string]$RepoRoot = (Resolve-Path ".").Path,
  [string]$OutFile = (Join-Path (Resolve-Path ".").Path "PROJECT_DUMP.txt"),
  [switch]$SkipDuplicateImports = $true,
  [int]$MaxFileBytes = 2MB
)

$ErrorActionPreference = "Stop"

function IsTextFile([string]$path) {
  $ext = [IO.Path]::GetExtension($path).ToLowerInvariant()
  # Add/adjust as needed
  $textExts = @(
    ".py",".md",".txt",".yml",".yaml",".json",".toml",".ini",".cfg",".env",
    ".dockerfile",".sh",".ps1",".psm1",".bat",".cmd",
    ".html",".css",".js",".ts",".tsx",".jsx",
    ".java",".cs",".go",".rs",".c",".cpp",".h",".hpp",
    ".sql",".xml",".properties",".gitignore",".gitattributes",".editorconfig"
  )
  if ($textExts -contains $ext) { return $true }
  if ([IO.Path]::GetFileName($path) -in @("Dockerfile","README","README.md")) { return $true }
  return $false
}

function ShouldExcludePath([string]$fullPath) {
  $p = $fullPath.Replace('\','/').ToLowerInvariant()
  $excludeSegments = @(
    "/.git/","/.idea/","/.vscode/","/node_modules/","/__pycache__/",
    "/.venv/","/venv/","/env/","/dist/","/build/","/target/",
    "/data/","/migrations/","/.pytest_cache/","/.mypy_cache/"
  )
  foreach ($seg in $excludeSegments) {
    if ($p.Contains($seg)) { return $true }
  }
  return $false
}

function ShouldExcludeFile([string]$fullPath) {
  $name = [IO.Path]::GetFileName($fullPath).ToLowerInvariant()
  # Avoid leaking secrets
  if ($name -in @(".env",".env.local",".env.development",".env.production","secrets.json","credentials.json")) { return $true }
  if ($name -match '\.pem$|\.key$|\.pfx$|\.p12$') { return $true }
  return $false
}

function Get-RelativePathCompat([string]$basePath, [string]$fullPath) {
  $base = (Resolve-Path $basePath).Path.TrimEnd('\','/')
  $full = (Resolve-Path $fullPath).Path
  if ($full.Length -ge $base.Length -and $full.Substring(0, $base.Length).ToLowerInvariant() -eq $base.ToLowerInvariant()) {
    $rel = $full.Substring($base.Length).TrimStart('\','/')
    return $rel.Replace('\','/')
  }
  # fallback: just return the full path (shouldn't happen inside RepoRoot)
  return $full.Replace('\','/')
}

function NormalizeImportLine([string]$line) {
  # crude normalization to dedupe common Python imports and JS/TS imports
  return ($line.Trim() -replace '\s+', ' ')
}

if (-not (Test-Path $RepoRoot)) {
  throw "RepoRoot not found: $RepoRoot"
}

Write-Host "RepoRoot: $RepoRoot"
Write-Host "OutFile : $OutFile"

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$writer = New-Object System.IO.StreamWriter($OutFile, $false, $utf8NoBom)

try {
  $writer.WriteLine("PROJECT DUMP")
  $writer.WriteLine("RepoRoot: $RepoRoot")
  $writer.WriteLine("Generated: $(Get-Date -Format o)")
  $writer.WriteLine("")

  $seenImports = New-Object 'System.Collections.Generic.HashSet[string]'
  $outFullPath = (Resolve-Path (Split-Path -Parent $OutFile) -ErrorAction SilentlyContinue)
  if ($outFullPath) {
    $outFullPath = (Join-Path $outFullPath.Path (Split-Path -Leaf $OutFile))
  } else {
    $outFullPath = (Resolve-Path $OutFile -ErrorAction SilentlyContinue).Path
  }

  $files = Get-ChildItem -Path $RepoRoot -Recurse -File | Sort-Object FullName
  foreach ($f in $files) {
    if (ShouldExcludePath $f.FullName) { continue }
    if (ShouldExcludeFile $f.FullName) { continue }
    if (-not (IsTextFile $f.FullName)) { continue }
    if ($f.Length -gt $MaxFileBytes) { continue }
    if ($outFullPath -and ((Resolve-Path $f.FullName).Path -eq $outFullPath)) { continue }

    $rel = Get-RelativePathCompat $RepoRoot $f.FullName
    $writer.WriteLine("================================================================")
    $writer.WriteLine("PATH: $rel")
    $writer.WriteLine("SIZE: $($f.Length) bytes")
    $writer.WriteLine("----------------------------------------------------------------")

    $lines = [IO.File]::ReadAllLines($f.FullName, $utf8NoBom)
    if ($SkipDuplicateImports) {
      foreach ($line in $lines) {
        $trim = $line.TrimStart()
        $isImport =
          ($trim -match '^(import\s+.+|from\s+\S+\s+import\s+.+)\s*$') -or
          ($trim -match '^import\s+.+from\s+.+\s*;\s*$') -or
          ($trim -match '^import\s+.+\s*;\s*$') -or
          ($trim -match '^(const|let|var)\s+.+\s*=\s*require\(.+\)\s*;\s*$')

        if ($isImport) {
          $norm = NormalizeImportLine $trim
          if ($seenImports.Contains($norm)) { continue }
          $null = $seenImports.Add($norm)
        }
        $writer.WriteLine($line)
      }
    } else {
      foreach ($line in $lines) {
        $writer.WriteLine($line)
      }
    }

    $writer.WriteLine("")
  }

  $writer.WriteLine("END OF DUMP")
} finally {
  $writer.Flush()
  $writer.Dispose()
}

Write-Host "Done. Wrote: $OutFile"

