#!/usr/bin/env bash

python3 -m pip install --user -r requirements-build.txt
python3 -m pip install --user -r requirements.txt
python3 -m PyInstaller -D -F -n "Batch-Image-Converter-Linux" --distpath ./ -c './src/main.py'