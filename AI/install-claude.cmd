@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM   Claude Code One-Click Installer (Windows)
REM   Supports proxy configuration
REM ============================================================

REM Default proxy settings
set "PROXY_HOST=127.0.0.1"
set "PROXY_PORT=7890"
set "SET_PROXY_ENV=1"

REM Parse arguments
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--proxy" (
    set "PROXY_HOST=%~2"
    shift & shift
    goto parse_args
)
if /i "%~1"=="--port" (
    set "PROXY_PORT=%~2"
    shift & shift
    goto parse_args
)
if /i "%~1"=="--no-proxy" (
    set "PROXY_HOST="
    set "SET_PROXY_ENV=0"
    shift
    goto parse_args
)
if /i "%~1"=="--no-env" (
    set "SET_PROXY_ENV=0"
    shift
    goto parse_args
)
if /i "%~1"=="--help" goto show_help
if /i "%~1"=="-h" goto show_help
shift
goto parse_args
:args_done

REM Build proxy URL
if defined PROXY_HOST (
    set "PROXY_URL=http://%PROXY_HOST%:%PROXY_PORT%"
    set "CURL_PROXY=-x %PROXY_URL%"
) else (
    set "PROXY_URL="
    set "CURL_PROXY="
)

echo.
echo ============================================================
echo   Claude Code Installer
echo ============================================================
echo.
if defined PROXY_URL (
    echo   Proxy: %PROXY_URL%
) else (
    echo   Proxy: None (direct connection)
)
echo   Install Path: %USERPROFILE%\.claude\bin
echo.
echo ============================================================
echo.

REM Check curl
curl --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] curl not found. Please install curl first.
    exit /b 1
)

REM Create directories
set "CLAUDE_DIR=%USERPROFILE%\.claude"
set "DOWNLOAD_DIR=%CLAUDE_DIR%\downloads"
set "BIN_DIR=%CLAUDE_DIR%\bin"

if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

REM Get latest version
echo [1/5] Getting latest version...
curl %CURL_PROXY% -fsSL https://downloads.claude.ai/claude-code-releases/latest -o "%DOWNLOAD_DIR%\latest"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to get latest version. Check network or proxy.
    exit /b 1
)
set /p VERSION=<"%DOWNLOAD_DIR%\latest"
del "%DOWNLOAD_DIR%\latest"
echo       Version: %VERSION%

REM Detect platform
set "PLATFORM=win32-x64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "PLATFORM=win32-arm64"

REM Download binary
set "BINARY_URL=https://downloads.claude.ai/claude-code-releases/%VERSION%/%PLATFORM%/claude.exe"
set "BINARY_PATH=%DOWNLOAD_DIR%\claude-%VERSION%.exe"

echo [2/5] Downloading Claude Code (%PLATFORM%)...
echo       This may take a few minutes (~280MB)...
curl %CURL_PROXY% -fSL --connect-timeout 30 --max-time 600 --retry 3 --retry-delay 5 -o "%BINARY_PATH%" "%BINARY_URL%"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Download failed. Check your network connection.
    if exist "%BINARY_PATH%" del "%BINARY_PATH%"
    exit /b 1
)

REM Copy to bin directory
echo [3/5] Installing to %BIN_DIR%...
copy /y "%BINARY_PATH%" "%BIN_DIR%\claude.exe" >nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to copy file.
    exit /b 1
)

REM Cleanup
del "%BINARY_PATH%" >nul 2>&1

REM Configure PATH
echo [4/5] Configuring PATH...
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "CURRENT_PATH=%%b"
echo %CURRENT_PATH% | findstr /i /c:".claude\bin" >nul
if %ERRORLEVEL% neq 0 (
    setx PATH "%CURRENT_PATH%;%BIN_DIR%" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo       PATH updated successfully.
    ) else (
        echo       [WARN] Failed to update PATH. Please add manually: %BIN_DIR%
    )
) else (
    echo       PATH already contains claude.
)

REM Set proxy environment variables
echo [5/5] Setting proxy environment variables...
if "%SET_PROXY_ENV%"=="1" (
    if defined PROXY_URL (
        setx HTTP_PROXY "%PROXY_URL%" >nul 2>&1
        setx HTTPS_PROXY "%PROXY_URL%" >nul 2>&1
        echo       HTTP_PROXY and HTTPS_PROXY set to %PROXY_URL%
    )
) else (
    echo       Skipped (--no-env specified).
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo   Claude Code %VERSION% installed to:
echo   %BIN_DIR%\claude.exe
echo.
echo   Open a NEW terminal window, then run:
echo   claude
echo.
if defined PROXY_URL (
    echo   Proxy configured: %PROXY_URL%
    echo.
)
echo ============================================================
echo.

REM Verify installation
"%BIN_DIR%\claude.exe" --version

exit /b 0

:show_help
echo.
echo Claude Code One-Click Installer
echo.
echo Usage: %~nx0 [options]
echo.
echo Options:
echo   --proxy HOST    Set proxy host (default: 127.0.0.1)
echo   --port PORT     Set proxy port (default: 7890)
echo   --no-proxy      Direct connection without proxy
echo   --no-env        Don't set permanent proxy environment variables
echo   -h, --help      Show this help message
echo.
echo Examples:
echo   %~nx0                          Use default proxy 127.0.0.1:7890
echo   %~nx0 --proxy 192.168.1.1 --port 1080
echo   %~nx0 --no-proxy               Direct connection
echo.
exit /b 0
