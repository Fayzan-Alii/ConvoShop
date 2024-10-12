@echo off

:: Change directory to the 'src' folder
cd src

:: Activate the Python virtual environment
call .\venv\Scripts\activate

:: Set the OpenAI API key environment variable
set OPENAI_API_KEY=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

:: Ensure required Python packages are installed (like openai)
python -m pip install -r D:\Work\FYP\chatgpt-app\chatgpt-app\src\requirements_oa.txt

:: Start the Flask app
python D:\Work\FYP\chatgpt-app\chatgpt-app\src\App_oa.py

:: Pause to keep the window open after execution
pause
