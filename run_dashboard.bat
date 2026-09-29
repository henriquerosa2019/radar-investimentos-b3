@echo off
title Radar B3 - Terminal de Acoes
echo ========================================================
echo   Iniciando Radar B3 - Terminal de Investimentos
echo ========================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
