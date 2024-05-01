python -m pip install --user -r requirements-build.txt
python -m pip install --user -r requirements.txt
python -m pip install --user pyinstaller_versionfile
python tools\versionfile_generator.py
python -m PyInstaller .\src\main.py --onefile --distpath ./ --icon=.\assets\logo.png -n="Batch-Image-Converter-Win64" --version-file versionfile.txt