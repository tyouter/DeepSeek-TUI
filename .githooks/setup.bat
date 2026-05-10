@echo off
REM Setup git hooks for DeepSeek TUI development
REM Run this once after cloning / checking out the dev branch.
echo ============================================
echo   Setting up git hooks...
echo ============================================
git config core.hooksPath .githooks
echo   Git hooks directory set to .githooks/
echo.
echo   Hooks installed:
echo     pre-commit - runs "python scripts/check.py quick" before each commit
echo     pre-push   - runs "python scripts/check.py full" before each push
echo.
echo   To skip hooks temporarily:
echo     git commit --no-verify
echo     git push   --no-verify
echo.
echo   Prerequisite: Python 3 on PATH
echo   Done.
