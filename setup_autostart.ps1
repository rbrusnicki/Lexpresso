# Lexpresso Auto-Start Setup Script
# This script creates a Windows Task Scheduler task to start Lexpresso automatically on boot
# Run this script as Administrator

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Lexpresso Auto-Start Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Get the current directory (where the script is located)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batchFile = Join-Path $scriptDir "start_lexpresso.bat"

# Check if the batch file exists
if (-not (Test-Path $batchFile)) {
    Write-Host "ERROR: start_lexpresso.bat not found in $scriptDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Task Scheduler settings
$taskName = "Lexpresso Server Auto-Start"
$taskDescription = "Automatically starts the Lexpresso language learning server on Windows startup"

Write-Host "Creating Task Scheduler task..." -ForegroundColor Yellow
Write-Host "Task Name: $taskName" -ForegroundColor Gray
Write-Host "Script Location: $batchFile" -ForegroundColor Gray
Write-Host ""

try {
    # Remove existing task if it exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # Create the action (what to run)
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batchFile`"" -WorkingDirectory $scriptDir

    # Create the trigger (when to run) - at system startup
    $trigger = New-ScheduledTaskTrigger -AtStartup

    # Create additional settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0)

    # Create the principal (run as SYSTEM or current user)
    # Using SYSTEM allows it to run without user login
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

    # Register the task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null

    Write-Host ""
    Write-Host "SUCCESS! Task created successfully." -ForegroundColor Green
    Write-Host ""
    Write-Host "The Lexpresso server will now start automatically when Windows boots." -ForegroundColor Green
    Write-Host ""
    Write-Host "Additional Information:" -ForegroundColor Cyan
    Write-Host "- The server runs as SYSTEM account" -ForegroundColor Gray
    Write-Host "- It will restart automatically if it crashes (up to 3 times)" -ForegroundColor Gray
    Write-Host "- It will work even if no user is logged in" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To verify the task:" -ForegroundColor Yellow
    Write-Host "1. Open Task Scheduler (press Win+R, type 'taskschd.msc')" -ForegroundColor Gray
    Write-Host "2. Look for '$taskName' in the task list" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To test it now (without rebooting):" -ForegroundColor Yellow
    Write-Host "Run: Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To remove the auto-start:" -ForegroundColor Yellow
    Write-Host "Run: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Read-Host "Press Enter to exit"
