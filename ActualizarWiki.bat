@echo off
title Actualizando Toys Zombies Wiki
color 0c

echo ===================================================
echo     Iniciando protocolo de actualizacion...
echo     Subiendo archivos de Toys Zombies a internet
echo ===================================================
echo.

:: Este comando le dice a MkDocs que construya la pagina y la suba a GitHub
mkdocs gh-deploy --force

echo.
echo ===================================================
echo   ¡Actualizacion completada con exito!
echo   Los cambios se veran reflejados en un par de minutos.
echo ===================================================
echo.
pause