@echo off

call .\venv\Scripts\activate.bat

echo Where python:
echo.
where python
echo.
echo Continue?

pause

.\venv\Scripts\python.exe -m pip install -U pip
.\venv\Scripts\python.exe -m pip install -U build

echo.
echo.
echo ============================================================
echo.
echo.

.\venv\Scripts\python.exe -m build
pause
