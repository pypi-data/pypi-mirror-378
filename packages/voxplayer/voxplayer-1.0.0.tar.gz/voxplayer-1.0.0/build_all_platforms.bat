@echo off
echo ========================================
echo VoxPlayer Cross-Platform Builder
echo ========================================
echo.

echo Detected platform: Windows
echo.

echo Starting build process...
echo.

echo Building source distribution...
if exist "build_source.sh" (
    echo Note: Source distribution build requires Linux/macOS
    echo Skipping source distribution build on Windows
) else (
    echo ERROR: build_source.sh not found
    goto :error
)

echo.
echo Building for Windows...
if exist "build_simple.bat" (
    call build_simple.bat
    if errorlevel 1 (
        echo ERROR: Windows build failed
        goto :error
    )
) else (
    echo ERROR: build_simple.bat not found
    goto :error
)

echo.
echo ========================================
echo Build process completed!
echo ========================================
echo.

echo Created files:
dir *.exe *.zip 2>nul

echo.
echo Installation instructions:
echo.
echo Windows:
echo   Run dist\VoxPlayer.exe
echo   Run register_file_associations.bat as Administrator
echo.
echo For other platforms, use the appropriate build script:
echo   - macOS: build_macos.sh
echo   - Debian/Ubuntu: build_debian.sh
echo   - Fedora/CentOS/RHEL: build_rpm.sh
echo   - Arch Linux: build_arch.sh
echo   - Source distribution: build_source.sh
echo.
echo For more information, see README.md
echo.
echo Build completed successfully! 🎬✨
goto :end

:error
echo.
echo Build failed! Please check the error messages above.
exit /b 1

:end
pause
