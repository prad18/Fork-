@echo off
echo ================================================================
echo                    Fork+ LLM Setup Script
echo ================================================================
echo.
echo This script will help you set up Ollama for local LLM parsing.
echo.

:: Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not installed or not in PATH
    echo.
    echo Please install Ollama from: https://ollama.ai/
    echo.
    echo Installation steps:
    echo 1. Download Ollama for Windows from https://ollama.ai/
    echo 2. Run the installer
    echo 3. Restart your terminal/command prompt
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama is installed
ollama --version
echo.

:: Check if Ollama service is running
echo 🔄 Checking if Ollama service is running...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama service is not running
    echo.
    echo Starting Ollama service...
    start "" ollama serve
    echo ⏳ Waiting for service to start...
    timeout /t 5 /nobreak >nul
    
    :: Check again
    ollama list >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Failed to start Ollama service
        echo Please start it manually: ollama serve
        pause
        exit /b 1
    )
)

echo ✅ Ollama service is running
echo.

:: List available models
echo 📋 Currently installed models:
ollama list
echo.

:: Check for recommended models
echo 🔄 Checking for recommended models...

set "model_found=false"

:: Check for llama3.2 first (recommended)
ollama list | findstr "llama3.2" >nul
if %errorlevel% equ 0 (
    echo ✅ Found llama3.2 model
    set "model_found=true"
    set "recommended_model=llama3.2"
) else (
    :: Check for llama3.1
    ollama list | findstr "llama3.1" >nul
    if %errorlevel% equ 0 (
        echo ✅ Found llama3.1 model
        set "model_found=true"
        set "recommended_model=llama3.1"
    ) else (
        :: Check for llama3
        ollama list | findstr "llama3" >nul
        if %errorlevel% equ 0 (
            echo ✅ Found llama3 model
            set "model_found=true"
            set "recommended_model=llama3"
        ) else (
            :: Check for any phi model
            ollama list | findstr "phi" >nul
            if %errorlevel% equ 0 (
                echo ✅ Found phi model
                set "model_found=true"
                set "recommended_model=phi"
            )
        )
    )
)

if "%model_found%"=="false" (
    echo ⚠️ No recommended models found
    echo.
    echo Recommended models for invoice parsing:
    echo - llama3.2:latest ^(best overall, ~2GB^)
    echo - llama3.1:latest ^(good performance, ~4.7GB^)
    echo - phi3:latest ^(lightweight, ~2.3GB^)
    echo.
    
    set /p install_model="Would you like to install llama3.2? (y/n): "
    if /i "%install_model%"=="y" (
        echo.
        echo 📥 Installing llama3.2... This may take a few minutes.
        echo.
        ollama pull llama3.2:latest
        if %errorlevel% equ 0 (
            echo ✅ llama3.2 installed successfully
            set "recommended_model=llama3.2"
        ) else (
            echo ❌ Failed to install llama3.2
            echo Please install manually: ollama pull llama3.2
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Please install a model manually:
        echo   ollama pull llama3.2:latest
        echo   ollama pull llama3.1:latest
        echo   ollama pull phi3:latest
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 🧪 Testing the model with a simple prompt...
echo.

:: Test the model
echo Testing %recommended_model%... | ollama run %recommended_model% "Please respond with just 'OK' if you can process this message."

if %errorlevel% equ 0 (
    echo.
    echo ✅ Model test successful!
) else (
    echo.
    echo ❌ Model test failed
    echo The model may still be downloading or there's an issue
)

echo.
echo ================================================================
echo                        Setup Complete!
echo ================================================================
echo.
echo ✅ Ollama is installed and running
echo ✅ Model '%recommended_model%' is available
echo.
echo You can now use the LLM invoice parser in Fork+
echo.
echo Test commands:
echo   ollama run %recommended_model%
echo   ollama list
echo   ollama serve ^(if service stops^)
echo.
echo Next steps:
echo 1. Make sure your FastAPI backend is running
echo 2. Test the parser at: POST /api/invoices/test/parse-text
echo 3. Check service status at: GET /api/invoices/service/status
echo.
pause
