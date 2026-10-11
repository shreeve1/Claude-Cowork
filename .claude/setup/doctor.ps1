<#
Read-only check of this workspace for Windows computers without Python. Changes nothing.

    powershell -ExecutionPolicy Bypass -File .claude\setup\doctor.ps1              everyday check
    powershell -ExecutionPolicy Bypass -File .claude\setup\doctor.ps1 -Migration   the setup gate

Run from the workspace root. Same structure and ledger rules as doctor.py (MIGRATING.md, "What the check enforces").
The memory audit and the team profile check need Python and are skipped here. Works in Windows PowerShell 5.1 and 7.
#>
param([switch]$Migration)
$ErrorActionPreference = 'Stop'
$Root = (Get-Location).Path
$Ledger = 'memory/migration-ledger.md'
$Outcomes = @('moved', 'merged', 'dropped', 'none')
$OldLayout = @('.opencode', 'opencode.jsonc', '.agents', 'AGENTS.md')
$RootExtraFiles = @('MANIFEST.json', '.gitignore', '.mcp.json', '.DS_Store', 'Thumbs.db', '1.Activity.md')
$RootExtraDirs = @('.git', '.claude', '.codex')
$Pointers = @('GEMINI.md')
$Skip = @('.git', 'node_modules', '__pycache__', '.venv', '.DS_Store', 'Thumbs.db')
$script:Problems = 0

function Report([bool]$Ok, [string]$Label, [string]$Fix = '') {
    if (-not $Ok) { $script:Problems++ }
    $line = $(if ($Ok) { 'ok    ' } else { 'FIX   ' }) + $Label
    if (-not $Ok -and $Fix) { $line += "`n      -> $Fix" }
    Write-Output $line
}
function Info([string]$Text) { Write-Output "info  $Text" }
function Norm([string]$P) {
    if (-not $P) { return '' }
    $p = $P.Trim().Replace('\', '/')
    if ($p.StartsWith('./')) { $p = $p.Substring(2) }
    return $p.Trim('/')
}
function Get-LfSha([string]$Path) {
    $bytes = [IO.File]::ReadAllBytes($Path)
    $out = New-Object System.Collections.Generic.List[byte]
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        if ($bytes[$i] -eq 13 -and $i + 1 -lt $bytes.Length -and $bytes[$i + 1] -eq 10) { continue }
        $out.Add($bytes[$i])
    }
    $sha = [Security.Cryptography.SHA256]::Create()
    return (($sha.ComputeHash($out.ToArray()) | ForEach-Object { $_.ToString('x2') }) -join '')
}
function Invoke-Git([string[]]$GitArgs) {
    $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $out = & git @GitArgs 2>$null
    $code = $LASTEXITCODE; $ErrorActionPreference = $prev
    return @{ Out = ($out -join "`n").Trim(); Code = $code }
}
function Read-Text([string]$Path) { return [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8) }

# --- tools
$repo = $false
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Info 'git not found: no version history and no commit checks (the workspace still works)'
} else {
    $repo = (Invoke-Git @('rev-parse', '--is-inside-work-tree')).Out -eq 'true'
    Report $repo 'workspace has its own git history' 'run `git init` here (INSTALL.md)'
    if ($repo) {
        Report ((Invoke-Git @('config', '--local', '--get', 'hooks.publishRelease')).Out -ne 'true') `
            'this is a workspace, not the Release repo itself' 'copy the Release into a new folder and work there (INSTALL.md)'
        if ($Migration) {
            Report (-not (Invoke-Git @('remote')).Out) 'no remote copied from the Release' `
                'this folder was cloned: copy its files without .git into a new folder (INSTALL.md)'
        }
        if (Test-Path -LiteralPath (Join-Path $Root '.githooks') -PathType Container) {
            $hp = (Invoke-Git @('config', 'core.hooksPath')).Out
            $py = $false
            if (Get-Command python3 -ErrorAction SilentlyContinue) {
                $v = & python3 -c "import sys; print(sys.version_info >= (3, 10))" 2>$null
                $py = ($LASTEXITCODE -eq 0 -and "$v".Trim() -eq 'True')
            }
            if ($py) {
                Report ($hp -eq '.githooks') 'git hooks switched on (secret scan, memory check, push protection)' 'run `git config core.hooksPath .githooks`'
            } else {
                Info 'python3 3.10+ not found: the secret scan and memory check cannot run'
                Report ($hp -eq '.githooks/nopython') 'push protection switched on without Python' `
                    'run `git config core.hooksPath .githooks/nopython`; never leave the hooks off'
            }
        }
    }
}

# --- manifest and shipped files
$files = @{}
$manifestPath = Join-Path $Root 'MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    Report $false 'MANIFEST.json present' 'this folder is not a copy of a Release (INSTALL.md)'
} else {
    $m = (Read-Text $manifestPath) | ConvertFrom-Json
    foreach ($prop in $m.files.PSObject.Properties) { $files[$prop.Name] = $prop.Value }
    $missing = @($files.Keys | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf) } | Sort-Object)
    $changed = @($files.Keys | Where-Object {
            $files[$_].class -eq 'merge' -and (Test-Path -LiteralPath (Join-Path $Root $_) -PathType Leaf) -and
            (Get-LfSha (Join-Path $Root $_)) -ne $files[$_].sha256 } | Sort-Object)
    if ($Migration) {
        Report ($missing.Count -eq 0) 'every shipped file is present' ('restore from the Release: ' + (($missing | Select-Object -First 8) -join ', '))
        Report ($changed.Count -eq 0) 'shipped files arrive unchanged' ('restore from the Release; personal rules go to memory (MIGRATING.md): ' + (($changed | Select-Object -First 8) -join ', '))
    } else {
        if ($missing.Count) { Info "$($missing.Count) shipped file(s) removed by the owner, e.g. $($missing[0])" }
        if ($changed.Count) { Info "$($changed.Count) shipped file(s) edited by the owner, e.g. $($changed[0])" }
    }

    # --- layout
    $topFiles = @($files.Keys | Where-Object { $_ -notmatch '/' })
    $topDirs = @($files.Keys | Where-Object { $_ -match '/' } | ForEach-Object { $_.Split('/')[0] }) + $RootExtraDirs
    $doc = Join-Path $Root 'memory/preferences/document-scaffolding.md'
    if (Test-Path -LiteralPath $doc) {
        $topDirs += [regex]::Matches((Read-Text $doc), '`([A-Za-z0-9._-]+)/') | ForEach-Object { $_.Groups[1].Value }
    }
    $bad = @()
    foreach ($child in Get-ChildItem -LiteralPath $Root -Force | Sort-Object Name) {
        $name = $child.Name
        if ($OldLayout -contains $name) { $bad += "$name (old layout: move what it holds per MIGRATING.md, then delete it)" }
        elseif ($child.PSIsContainer -and ($topDirs -notcontains $name)) { $bad += "$name/ (not in the folder map memory/preferences/document-scaffolding.md)" }
        elseif (-not $child.PSIsContainer -and ($Pointers -contains $name)) {
            $t = Read-Text $child.FullName
            $lines = @($t -split "`n" | Where-Object { $_.Trim() })
            if ($t -notmatch 'AGENTS\.md' -or $lines.Count -gt 10) { $bad += "$name (only a short pointer to CLAUDE.md is allowed)" }
        }
        elseif (-not $child.PSIsContainer -and ($topFiles -notcontains $name) -and ($RootExtraFiles -notcontains $name)) {
            $bad += "$name (no loose files in the root; see the folder map)"
        }
    }
    Report ($bad.Count -eq 0) 'workspace root matches the shipped layout' ($bad -join '; ')
    $skills = Join-Path $Root '.claude/skills'
    $broken = @()
    if (Test-Path -LiteralPath $skills) {
        $broken = @(Get-ChildItem -LiteralPath $skills -Directory | Where-Object { -not (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md')) } | ForEach-Object Name)
    }
    Report ($broken.Count -eq 0) 'every skill folder has a SKILL.md' ($broken -join ', ')
}

# --- ledger
$ledgerPath = Join-Path $Root $Ledger
if (-not (Test-Path -LiteralPath $ledgerPath)) {
    Report (-not $Migration) 'migration ledger present' "write $Ledger (MIGRATING.md, step 1)"
} else {
    $text = Read-Text $ledgerPath
    $sources = @([regex]::Matches($text, '(?m)^Source:\s*(.+)$') | ForEach-Object { $_.Groups[1].Value.Trim() })
    $rows = @()
    foreach ($line in $text -split "`r?`n") {
        if (-not $line.TrimStart().StartsWith('|')) { continue }
        if ($line -match '^[\s|:\-]+$') { continue }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        if ($cells.Count -lt 4 -or $cells[0] -eq 'Source') { continue }
        $rows += , @($cells[0], $cells[1], $cells[2], $cells[3])
    }
    $mergeFiles = @($files.Keys | Where-Object { $files[$_].class -eq 'merge' })
    $bad = @()
    if ($rows.Count -eq 0) { $bad += 'no rows; a workspace with nothing to migrate has one row with outcome `none`' }
    if (($rows | Where-Object { $_[2] -eq 'none' }) -and $rows.Count -gt 1) { $bad += '`none` must be the only row' }
    foreach ($r in $rows) {
        $src, $dest, $outcome, $note = $r
        if ($Outcomes -notcontains $outcome) { $bad += "${src}: outcome ``$outcome`` is not one of $($Outcomes -join ', ')" }
        elseif ($outcome -eq 'dropped' -and -not $note) { $bad += "${src}: dropped needs a reason in Note" }
        elseif ($outcome -in @('moved', 'merged')) {
            if (-not $dest.Trim()) { $bad += "${src}: $outcome needs a Destination" }
            foreach ($d in ($dest.Split(',') | ForEach-Object { Norm ($_.Split('#')[0]) } | Where-Object { $_ })) {
                if (-not (Test-Path -LiteralPath (Join-Path $Root $d))) { $bad += "${src}: destination $d does not exist" }
                elseif ($mergeFiles -contains $d) { $bad += "${src}: $d is a shipped file; personal content goes to memory or your own skill" }
                elseif ($OldLayout -contains $d.Split('/')[0]) { $bad += "${src}: $d is old layout" }
            }
        }
    }
    foreach ($s in $sources) {
        if (-not (Test-Path -LiteralPath $s)) { $bad += "Source $s cannot be read here (attach or copy it, then rerun)"; continue }
        $base = Norm $s
        $listed = @($rows | ForEach-Object {
                $n = Norm $_[0]
                if ($n.ToLower().StartsWith($base.ToLower())) { $n = $n.Substring($base.Length).Trim('/') }
                if ($_[0].TrimEnd().EndsWith('/') -or $_[0].TrimEnd().EndsWith('\')) { $n += '/' }
                $n })
        $item = Get-Item -LiteralPath $s
        if ($item.PSIsContainer) {
            $baseFull = $item.FullName.TrimEnd('\', '/')
            $found = @(Get-ChildItem -LiteralPath $s -Recurse -File -Force | Where-Object {
                    $rel = $_.FullName.Substring($baseFull.Length + 1).Replace('\', '/')
                    -not ($rel.Split('/') | Where-Object { $Skip -contains $_ }) } |
                ForEach-Object { $_.FullName.Substring($baseFull.Length + 1).Replace('\', '/') })
        } else { $found = @($item.Name) }
        $missed = @($found | Where-Object { $f = $_; -not ($listed | Where-Object { $f -eq $_ -or ($_.EndsWith('/') -and $f.StartsWith($_)) }) })
        if ($missed.Count) { $bad += "Source ${s}: $($missed.Count) file(s) have no row, e.g. " + (($missed | Select-Object -First 5) -join ', ') }
    }
    if ($Migration -and $sources.Count -eq 0 -and -not ($rows | Where-Object { $_[2] -eq 'none' })) {
        $bad += 'no `Source:` line: list every old folder or file migrated from'
    }
    Report ($bad.Count -eq 0) 'migration ledger complete' (($bad | Select-Object -First 15) -join "`n      -> ")
    $dropped = @($rows | Where-Object { $_[2] -eq 'dropped' })
    if ($dropped.Count) { Info "$($dropped.Count) item(s) dropped; the owner must have agreed to each (see $Ledger)" }
}

Info 'memory audit and team profile checks need Python; skipped here'
if ($script:Problems) { Write-Output "`n$($script:Problems) thing(s) to fix."; exit 1 }
Write-Output "`nAll checks passed."
exit 0
