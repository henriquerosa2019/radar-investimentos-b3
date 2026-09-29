@echo off
title Enviar Radar B3 para o GitHub
echo =====================================================================
echo   Enviando Radar Investimentos B3 para o seu GitHub
echo   Destino: https://github.com/henriquerosarj/radar-investimentos-b3
echo =====================================================================
echo.
cd /d "%~dp0"
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo =====================================================================
    echo   SUCESSO! O codigo ja esta no seu GitHub.
    echo   Agora va em https://share.streamlit.io para publicar na Web!
    echo =====================================================================
) else (
    echo =====================================================================
    echo   Ops! Verifique se voce ja criou o repositorio 'radar-investimentos-b3'
    echo   no link: https://github.com/new
    echo =====================================================================
)
pause
