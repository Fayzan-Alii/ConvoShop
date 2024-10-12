@echo off

:: Change directory to the 'src' folder
cd src

:: Activate the Python virtual environment
call .\venv\Scripts\activate

:: Ensure required Python packages are installed (like transformers, flask, flask_cors)
python -m pip install -r D:\Work\FYP\chatgpt-app\chatgpt-app\src\requirements_hf.txt

:: Start the Flask app using Hugging Face model
python D:\Work\FYP\chatgpt-app\chatgpt-app\src\App_hf.py

:: Pause to keep the window open after execution
pause
