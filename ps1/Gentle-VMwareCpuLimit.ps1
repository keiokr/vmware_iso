$ErrorActionPreference = 'Continue'
$log = 'C:\ProgramData\Codex\Gentle-VMwareCpuLimit.log'

function Write-Log([string]$msg) {
  Add-Content -Path $log -Value ('{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg) -Encoding UTF8
}

function Get-HostCpuLoad {
  try {
    $sample = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 2 -ErrorAction Stop).CounterSamples |
      Select-Object -Last 1 -ExpandProperty CookedValue
    return [double]$sample
  } catch {
    try {
      $vals = Get-CimInstance Win32_Processor -ErrorAction Stop | Select-Object -ExpandProperty LoadPercentage
      if ($vals) { return [double](($vals | Measure-Object -Average).Average) }
    } catch {}
  }
  return 0.0
}

function Set-GlobalVmwareAffinity {
  param(
    [IntPtr]$Mask,
    [string]$ModeText,
    [double]$Load
  )

  Get-Process -Name 'vmware-vmx','mksSandbox' -ErrorAction SilentlyContinue | ForEach-Object {
    $p = $_
    $age = 0
    try { $age = ((Get-Date) - $p.StartTime).TotalSeconds } catch { $age = 0 }

    # Avoid touching boot/initialization stage.
    if ($age -lt 120) { return }

    try {
      if ($p.ProcessorAffinity -ne $Mask) {
        $old = $p.ProcessorAffinity
        $p.ProcessorAffinity = $Mask
        Write-Log ("STANDARD set {0} PID={1} age={2:n0}s hostCpu={3:n1}% mode={4} oldMask={5} newMask={6}" -f $p.ProcessName,$p.Id,$age,$Load,$ModeText,$old,$Mask)
      }
    } catch {
      Write-Log ("FAILED {0} PID={1}: {2}" -f $p.ProcessName,$p.Id,$_.Exception.Message)
    }
  }
}

Write-Log 'STANDARD GLOBAL limiter started. <=60%=CPU0-7 total 8 CPUs; >60%=CPU0-5 total 6 CPUs; process age >=120s.'

while ($true) {
  try {
    $load = Get-HostCpuLoad
    if ($load -gt 60) {
      Set-GlobalVmwareAffinity -Mask ([IntPtr]0x3F) -ModeText '6cpu-global-over60' -Load $load
    } else {
      Set-GlobalVmwareAffinity -Mask ([IntPtr]0xFF) -ModeText '8cpu-global-normal' -Load $load
    }
  } catch {
    Write-Log ("Loop error: {0}" -f $_.Exception.Message)
  }

  Start-Sleep -Seconds 10
}
