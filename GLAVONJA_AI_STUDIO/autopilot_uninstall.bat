@echo off
schtasks /Delete /F /TN "GLAVONJA Autopilot"
schtasks /Delete /F /TN "GLAVONJA Studio"
echo Autopilot removed. Your projects and videos are untouched.
pause
