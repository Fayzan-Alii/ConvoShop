@echo off

call .\venv\Scripts\activate

python -m pip install -r requirements.txt

python App.py

pause
