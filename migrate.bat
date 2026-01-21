@echo off
REM Database Migration Helper Script for Windows
REM This script provides shortcuts for common Flask-Migrate operations

setlocal enabledelayedexpansion

set FLASK_APP=run:app
set VENV_PYTHON=.venv\Scripts\python
set VENV_FLASK=.venv\Scripts\flask

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .venv
    echo Please create a virtual environment first: python -m venv .venv
    exit /b 1
)

REM Parse command
set COMMAND=%1

if "%COMMAND%"=="" goto :usage
if "%COMMAND%"=="help" goto :usage
if "%COMMAND%"=="init" goto :init
if "%COMMAND%"=="migrate" goto :migrate
if "%COMMAND%"=="upgrade" goto :upgrade
if "%COMMAND%"=="downgrade" goto :downgrade
if "%COMMAND%"=="current" goto :current
if "%COMMAND%"=="history" goto :history
if "%COMMAND%"=="stamp" goto :stamp
if "%COMMAND%"=="reset" goto :reset

echo [ERROR] Unknown command: %COMMAND%
goto :usage

:usage
echo Database Migration Helper Script
echo.
echo Usage: migrate.bat [command]
echo.
echo Commands:
echo     init        Initialize migrations (first time setup)
echo     migrate     Create a new migration from model changes
echo     upgrade     Apply all pending migrations
echo     downgrade   Revert last migration
echo     current     Show current migration version
echo     history     Show migration history
echo     stamp       Mark database as being at a specific revision
echo     reset       Reset database (WARNING: destroys all data)
echo     help        Show this help message
echo.
echo Examples:
echo     migrate.bat migrate "Add email_verified field"
echo     migrate.bat upgrade
echo     migrate.bat downgrade
echo     migrate.bat current
echo.
exit /b 0

:init
echo [INFO] Initializing Flask-Migrate...
%VENV_FLASK% --app %FLASK_APP% db init
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Migrations initialized successfully!
) else (
    echo [ERROR] Failed to initialize migrations
    exit /b 1
)
exit /b 0

:migrate
set MESSAGE=%~2
if "%MESSAGE%"=="" (
    echo [ERROR] Migration message required
    echo Usage: migrate.bat migrate "Description of changes"
    exit /b 1
)
echo [INFO] Creating new migration: %MESSAGE%
%VENV_FLASK% --app %FLASK_APP% db migrate -m "%MESSAGE%"
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Migration created successfully!
    echo [WARN] Please review the generated migration file before applying it.
) else (
    echo [ERROR] Failed to create migration
    exit /b 1
)
exit /b 0

:upgrade
echo [INFO] Applying pending migrations...
%VENV_FLASK% --app %FLASK_APP% db upgrade
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Migrations applied successfully!
) else (
    echo [ERROR] Failed to apply migrations
    exit /b 1
)
exit /b 0

:downgrade
echo [WARN] Reverting last migration...
set /p CONFIRM="Are you sure? (y/N): "
if /i "%CONFIRM%"=="y" (
    %VENV_FLASK% --app %FLASK_APP% db downgrade
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Migration reverted successfully!
    ) else (
        echo [ERROR] Failed to revert migration
        exit /b 1
    )
) else (
    echo [INFO] Downgrade cancelled.
)
exit /b 0

:current
echo [INFO] Current migration version:
%VENV_FLASK% --app %FLASK_APP% db current
exit /b 0

:history
echo [INFO] Migration history:
%VENV_FLASK% --app %FLASK_APP% db history
exit /b 0

:stamp
set REVISION=%2
if "%REVISION%"=="" set REVISION=head
echo [INFO] Stamping database at revision: %REVISION%
%VENV_FLASK% --app %FLASK_APP% db stamp %REVISION%
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Database stamped successfully!
) else (
    echo [ERROR] Failed to stamp database
    exit /b 1
)
exit /b 0

:reset
echo [ERROR] WARNING: This will destroy all data in the database!
set /p CONFIRM="Are you absolutely sure? Type 'yes' to confirm: "
if "%CONFIRM%"=="yes" (
    echo [WARN] Resetting database...
    echo [INFO] Please run these MySQL commands manually:
    echo.
    echo mysql -u root -p -e "DROP DATABASE IF EXISTS bjj_school; CREATE DATABASE bjj_school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo.
    echo Then run: migrate.bat upgrade
    echo.
) else (
    echo [INFO] Reset cancelled.
)
exit /b 0
