@echo off
chcp 65001 >nul
cd /d "%~dp0"
:menu
echo.
echo =========================================
echo   Mulight Grok Bot Efficiency Kit v1.0
echo =========================================
echo 1. Check environment (offline)
echo 2. Analyze example Routine schedule (offline)
echo 3. Check a BSC CA (uses internet)
echo 4. Check BSC RPC logs (requires config)
echo 5. Scan new BSC pairs once (requires config)
echo 6. Start LOCAL-only live monitor (requires config)
echo 7. Send ONE Grok Bot webhook test (usage cost!)
echo 0. Exit
echo.
set /p CHOICE=Choose 0-7: 
if "%CHOICE%"=="1" python -m grok_kit doctor
if "%CHOICE%"=="2" python -m grok_kit audit examples/routines.example.json
if "%CHOICE%"=="3" (
  set /p CA=Paste BSC contract address: 
  call :checkca
)
if "%CHOICE%"=="4" python -m grok_kit doctor-logs
if "%CHOICE%"=="5" python -m grok_kit watch --once
if "%CHOICE%"=="6" python -m grok_kit watch
if "%CHOICE%"=="7" (
  echo WARNING: This sends a real Grok Bot Routine event and consumes usage.
  set /p CONFIRM=Type YES to continue: 
  call :checkwebhook
)
if "%CHOICE%"=="0" exit /b
pause
goto menu
:checkca
if not "%CA%"=="" python -m grok_kit ca "%CA%"
exit /b
:checkwebhook
if "%CONFIRM%"=="YES" python -m grok_kit test-webhook
exit /b
