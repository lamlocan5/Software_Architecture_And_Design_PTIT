@echo off
REM Script to setup media directories and copy default images

echo Creating media directories...
if not exist media mkdir media
if not exist media\books mkdir media\books
if not exist media\avatars mkdir media\avatars

echo Copying default images...
copy /Y "C:\Users\Admin\Downloads\anh1.png" "media\books\default.png"
copy /Y "C:\Users\Admin\Downloads\anh1.png" "media\avatars\default.png"

echo.
echo Verifying files...
dir media\books\default.png
dir media\avatars\default.png

echo.
echo ✅ Done! Default images have been set up.
echo.
echo To update existing database records, run:
echo   python manage.py shell ^< set_default_images.py
echo.
pause
