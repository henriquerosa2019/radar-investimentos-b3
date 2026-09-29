@echo off
title Enviar Radar B3 para o GitHub
echo =====================================================================
echo   Enviando Radar Investimentos B3 para o seu GitHub
echo   Destino: https://github.com/henriquerosa2019/radar-investimentos-b3
echo =====================================================================
echo.
cd /d "%~dp0"
git add .
git commit -m "feat: complete dashboard with streamlit_app.py and app.py"
git branch -M main
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo =====================================================================
    echo   SUCESSO! O codigo ja esta no seu GitHub!
    echo   Agora volte no navegador (share.streamlit.io/deploy) e de um F5!
    echo =====================================================================
) else (
    echo =====================================================================
    echo   Ops! Ocorreu um erro no envio. Verifique o terminal acima.
    echo =====================================================================
)
pause
