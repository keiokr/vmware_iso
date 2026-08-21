$ErrorActionPreference = 'SilentlyContinue'
function Remove-OldFiles([string]$Path) {
    if (Test-Path $Path) {
        Get-ChildItem -LiteralPath $Path -Force -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}
Remove-OldFiles $env:TEMP
Remove-OldFiles 'C:\Windows\Temp'
Remove-OldFiles 'C:\Windows\SoftwareDistribution\Download'
Start-Process -FilePath 'Dism.exe' -ArgumentList '/Online','/Cleanup-Image','/StartComponentCleanup','/Quiet' -Wait -WindowStyle Hidden
Start-Process -FilePath 'defrag.exe' -ArgumentList 'C:','/O','/H' -Wait -WindowStyle Hidden
'cleanup-complete' | Set-Content -Path 'C:\ProgramData\Codex\cleanup.last' -Encoding ascii
