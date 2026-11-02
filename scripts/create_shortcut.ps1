$wshShell = New-Object -ComObject WScript.Shell
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$projectDir = (Get-Item -Path $PSScriptRoot).Parent.FullName

$shortcutPath = Join-Path $desktopPath "Flow Voice AI.lnk"
$targetPath = Join-Path $projectDir "Flow Voice AI.vbs"
$iconPath = Join-Path $projectDir "assets\icon.ico"

$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $projectDir
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Flow Voice AI"
$shortcut.Save()

Write-Host "Atalho criado com sucesso na Area de Trabalho: $shortcutPath"
