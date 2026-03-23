@echo off
title Actualizando Toy Zombies Página Oficial
color 0c

echo ===================================================
echo     1. Construyendo y subiendo la pagina web...
echo ===================================================
mkdocs gh-deploy --force

echo.
echo ===================================================
echo     2. Guardando textos en el repositorio...
echo ===================================================
git add .
git commit -m "Actualizacion de la página oficial"
git push origin main

echo.
echo ===================================================
echo   ¡Todo actualizado y guardado con exito!
echo   Recuerda presionar Ctrl + F5 en tu navegador.
echo ===================================================
echo.
pause