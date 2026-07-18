# setup_scheduler.ps1
# Set up a Windows Task Scheduler task to run the Snapchat Streak Automation daily.

$ScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "snapchat_streak.py"

# Default run time
$Time = "10:00"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " Snapchat Streak Automation Task Registration " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will register a Windows Scheduled Task to run snapchat_streak.py"
Write-Host "every day at a specified time."
Write-Host "Important: The task will run in your interactive user session so it can"
Write-Host "interact with the Android Emulator GUI."
Write-Host ""

$InputTime = Read-Host "Enter daily execution time (HH:MM, default: 10:00)"
if ($InputTime -and $InputTime -match "^\d{2}:\d{2}$") {
    $Time = $InputTime
} else {
    Write-Host "Using default time: $Time" -ForegroundColor Yellow
}

$TaskName = "SnapchatStreakAutomation"

# Define task action
$Action = New-ScheduledTaskAction -Execute "python" -Argument "`"$ScriptPath`"" -WorkingDirectory $PSScriptRoot

# Define daily trigger
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time

# Define principal to run interactively in the current user's session (essential for UI automation)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Define settings (allow running on battery power)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register/Overwrite task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force

Write-Host ""
Write-Host "✅ Scheduled Task '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "It is scheduled to run daily at: $Time" -ForegroundColor Green
Write-Host "Note: Ensure your Android Emulator is open and Snapchat is logged in at that time." -ForegroundColor Yellow
