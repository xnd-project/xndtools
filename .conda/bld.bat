cd "%RECIPE_DIR%\..\" || exit 1
"%PYTHON%" setup.py install || exit 1
if not exist "%RECIPE_DIR%\test" mkdir "%RECIPE_DIR%\test"
copy /y test\test_*.py "%RECIPE_DIR%\test"
