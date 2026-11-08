param([string]$Version = '')
$ErrorActionPreference = 'Stop'
$devAtlasProject = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if (-not $Version) {
    $devAtlasPython = Join-Path $devAtlasProject '.venv\Scripts\python.exe'
    $Version = & $devAtlasPython -c "import sys; sys.path.insert(0,sys.argv[1]); from devatlas import __version__; print(__version__)" $devAtlasProject
    if ($LASTEXITCODE -ne 0) { throw 'Impossibile leggere la versione del progetto.' }
}
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw 'Versione non valida.' }
$devAtlasExecutable = Join-Path $devAtlasProject ('dist\DevAtlas-' + $Version + '\DevAtlas.exe')
if (-not (Test-Path -LiteralPath $devAtlasExecutable -PathType Leaf)) { throw 'Compilare la versione prima di aggiornare il collegamento.' }
$devAtlasShortcutPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'DevAtlas.lnk'
$devAtlasShell = New-Object -ComObject WScript.Shell
$devAtlasShortcut = $devAtlasShell.CreateShortcut($devAtlasShortcutPath)
if (Test-Path -LiteralPath $devAtlasShortcutPath) {
    $devAtlasPrevious = [IO.Path]::GetFullPath($devAtlasShortcut.TargetPath)
    $devAtlasPrefix = $devAtlasProject.TrimEnd('\') + '\'
    if (-not $devAtlasPrevious.StartsWith($devAtlasPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Il collegamento esistente punta fuori dal progetto: non viene sostituito.'
    }
}
$devAtlasShortcut.TargetPath = $devAtlasExecutable
$devAtlasShortcut.WorkingDirectory = [IO.Path]::GetDirectoryName($devAtlasExecutable)
$devAtlasShortcut.IconLocation = $devAtlasExecutable + ',0'
$devAtlasShortcut.Description = 'DevAtlas ' + $Version + ' — Atlante del Codice offline'
$devAtlasShortcut.WindowStyle = 1
$devAtlasShortcut.Save()
$devAtlasVerified = $devAtlasShell.CreateShortcut($devAtlasShortcutPath)
if ($devAtlasVerified.TargetPath -ne $devAtlasExecutable) { throw 'Verifica del collegamento non riuscita.' }
[PSCustomObject]@{ Shortcut=$devAtlasShortcutPath; Target=$devAtlasVerified.TargetPath; Icon=$devAtlasVerified.IconLocation } | ConvertTo-Json -Compress

