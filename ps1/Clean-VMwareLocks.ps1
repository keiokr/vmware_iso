$ErrorActionPreference = "Continue"
$log = "C:\ProgramData\Codex\Clean-VMwareLocks.log"
function Log($m) {
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
    Add-Content -Path $log -Value $line -Encoding UTF8
}

Log "=== VMware lock cleanup start ==="

$running = Get-Process -Name "vmware-vmx","mksSandbox" -ErrorAction SilentlyContinue
if ($running) {
    Log "VMware backend process is running; skip lock cleanup to avoid corrupting active VMs."
    $running | ForEach-Object { Log ("running: {0} PID={1}" -f $_.ProcessName, $_.Id) }
    Log "=== VMware lock cleanup skipped ==="
    exit 0
}

$root = "D:\game_iso"
if (-not (Test-Path -LiteralPath $root)) {
    Log "Root not found: $root"
    Log "=== VMware lock cleanup end ==="
    exit 0
}

$pcRoots = Get-ChildItem -LiteralPath $root -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^pc\d+$" }

$removed = 0
foreach ($pc in $pcRoots) {
    $items = Get-ChildItem -LiteralPath $pc.FullName -Force -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\.lck($|\\)" } |
        Sort-Object FullName -Descending
    foreach ($item in $items) {
        try {
            Log ("remove lock: {0}" -f $item.FullName)
            Remove-Item -LiteralPath $item.FullName -Recurse -Force -ErrorAction Stop
            $removed++
        } catch {
            Log ("failed: {0} :: {1}" -f $item.FullName, $_.Exception.Message)
        }
    }
}

Log ("removed count: {0}" -f $removed)
Log "=== VMware lock cleanup end ==="
