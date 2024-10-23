@echo off

call .\venv\Scripts\activate

python -m pip install -r requirements.txt

@REM python App.py

uvicorn App:app --reload

pause
