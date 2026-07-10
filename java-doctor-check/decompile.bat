@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  decompile.bat - Unified decompilation tool launcher
REM  Supports: JDK 8/11/17/21/22/23/24/25
REM  Tools:    JADX (1.4.7 for JDK 8, 1.5.5 for JDK 11+), CFR, javap
REM ============================================================================

set "TOOLS_DIR=%~dp0"
set "CFR_JAR=%TOOLS_DIR%cfr.jar"
set "JADX_HOME=%TOOLS_DIR%jadx"
set "JADX_HOME_147=%TOOLS_DIR%jadx-1.4.7"
set "JAVA_CMD="

REM --- JDK Detection: highest version first (25 -> 8) ---
for %%V in (25 24 23 22 21 17 11) do (
    if not defined JAVA_CMD (
        for %%P in (
            "C:\Program Files\Java\jdk-%%V*"
            "C:\Program Files\Eclipse Adoptium\jdk-%%V*"
            "C:\Program Files\Amazon Corretto\jdk%%V*"
            "C:\Program Files\Microsoft\jdk-%%V*"
            "C:\Program Files\Zulu\zulu-%%V*"
            "D:\dev\Java\jdk-%%V*"
            "D:\dev\java\jdk-%%V*"
        ) do (
            if not defined JAVA_CMD (
                for /d %%D in (%%~P) do (
                    if not defined JAVA_CMD if exist "%%D\bin\java.exe" set "JAVA_CMD=%%D\bin\java.exe"
                )
            )
        )
    )
)

REM JDK 8 (special naming: jdk1.8* or jdk-8*)
if not defined JAVA_CMD (
    for %%P in (
        "C:\Program Files\Java\jdk1.8*"
        "C:\Program Files\Java\jdk-8*"
        "C:\Program Files\Eclipse Adoptium\jdk-8*"
        "C:\Program Files\Amazon Corretto\jdk1.8*"
        "C:\Program Files\Zulu\zulu-8*"
        "D:\dev\Java\jdk1.8*"
        "D:\dev\java\jdk1.8*"
        "D:\dev\Java\jdk-8*"
    ) do (
        if not defined JAVA_CMD (
            for /d %%D in (%%~P) do (
                if not defined JAVA_CMD if exist "%%D\bin\java.exe" set "JAVA_CMD=%%D\bin\java.exe"
            )
        )
    )
)

REM Fallback: JAVA_HOME -> PATH
if not defined JAVA_CMD if defined JAVA_HOME if exist "%JAVA_HOME%\bin\java.exe" set "JAVA_CMD=%JAVA_HOME%\bin\java.exe"
if not defined JAVA_CMD (
    where java >nul 2>&1
    if not errorlevel 1 for /f "delims=" %%i in ('where java') do if not defined JAVA_CMD set "JAVA_CMD=%%i"
)

if not defined JAVA_CMD (
    echo [ERROR] Java not found. Please install JDK 8-25.
    echo         Download: https://www.oracle.com/java/technologies/downloads/
    exit /b 1
)

REM --- Parse Java version ---
for /f "usebackq tokens=3" %%v in (`"%JAVA_CMD%" -version 2^>^&1`) do (set "RAW=%%~v" & goto :parsed)
:parsed
if "%RAW:~0,2%"=="1." (set "MAJOR=%RAW:~2,1%") else (for /f "tokens=1 delims=." %%m in ("%RAW%") do set "MAJOR=%%m")
echo [INFO] Java=%JAVA_CMD% ver=%RAW% major=%MAJOR%

REM --- JVM parameters by version ---
set "JVM=-Xms128M -Xmx512M"
if !MAJOR! GEQ 11 set "JVM=-Xms128M -XX:MaxRAMPercentage=70.0 -XX:+UseG1GC"
if !MAJOR! GEQ 21 set "JVM=%JVM% -XX:+UseStringDeduplication"

REM --- Select JADX version: JDK 8 -> 1.4.7, JDK 11+ -> 1.5.5 ---
set "USE_JADX=%JADX_HOME%"
if !MAJOR! LEQ 8 (
    if exist "%JADX_HOME_147%\bin\jadx.bat" (
        set "USE_JADX=%JADX_HOME_147%"
        echo [INFO] JDK 8 detected, using JADX 1.4.7
    ) else (
        echo [WARN] JDK 8 but JADX 1.4.7 not found, trying default
    )
) else (
    echo [INFO] JDK !MAJOR! detected, using JADX 1.5.5
)

REM --- Tool dispatch ---
set "TOOL=%~1"
if "%TOOL%"=="" (
    echo Usage: decompile [cfr^|jadx^|jadx-gui^|javap^|info] [args...]
    echo   Supported JDK: 8, 11, 17, 21, 22, 23, 24, 25
    exit /b 0
)
shift

if /i "%TOOL%"=="info" goto :cmd_info
if /i "%TOOL%"=="cfr" goto :cmd_cfr
if /i "%TOOL%"=="jadx" goto :cmd_jadx
if /i "%TOOL%"=="jadx-gui" goto :cmd_jadx_gui
if /i "%TOOL%"=="javap" goto :cmd_javap
echo [ERROR] Unknown tool: %TOOL% (available: cfr, jadx, jadx-gui, javap, info)
exit /b 1

REM === Commands ===

:cmd_info
echo ============================================
echo  Decompile Tool Environment
echo ============================================
echo  Java:    %JAVA_CMD%
echo  Version: %RAW% (major=%MAJOR%)
echo  JVM:     %JVM%
echo  JADX:    %USE_JADX%
if exist "%USE_JADX%\bin\jadx.bat" (echo  JADX:    [OK]) else (echo  JADX:    [NOT FOUND])
if exist "%JADX_HOME_147%\bin\jadx.bat" (echo  1.4.7:   [OK]) else (echo  1.4.7:   [NOT INSTALLED])
if exist "%CFR_JAR%" (echo  CFR:     [OK]) else (echo  CFR:     [NOT FOUND])
echo ============================================
exit /b 0

:cmd_cfr
if not exist "%CFR_JAR%" (echo [ERROR] CFR not found: %CFR_JAR% & exit /b 1)
"%JAVA_CMD%" %JVM% -jar "%CFR_JAR%" %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b !ERRORLEVEL!

:cmd_jadx
if not exist "%USE_JADX%\bin\jadx.bat" (echo [ERROR] JADX not found: %USE_JADX% & exit /b 1)
for %%i in ("%JAVA_CMD%") do set "JB=%%~dpi"
for %%i in ("!JB!..") do set "JAVA_HOME=%%~fi"
call "%USE_JADX%\bin\jadx.bat" %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b !ERRORLEVEL!

:cmd_jadx_gui
if not exist "%USE_JADX%\bin\jadx-gui.bat" (echo [ERROR] JADX GUI not found: %USE_JADX% & exit /b 1)
for %%i in ("%JAVA_CMD%") do set "JB=%%~dpi"
for %%i in ("!JB!..") do set "JAVA_HOME=%%~fi"
start "" "%USE_JADX%\bin\jadx-gui.bat" %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b 0

:cmd_javap
for %%i in ("%JAVA_CMD%") do set "JAVAP=%%~dpijavap.exe"
"!JAVAP!" %1 %2 %3 %4 %5 %6 %7 %8 %9
exit /b !ERRORLEVEL!
