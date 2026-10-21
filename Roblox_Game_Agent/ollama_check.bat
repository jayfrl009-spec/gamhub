@echo off
echo Checking Ollama root endpoint...
curl -sS http://localhost:11434/
echo.
echo Listing installed models...
ollama list
echo.
echo If the root endpoint did not say Ollama is running, start the Ollama app first.
echo If no vision model is listed, install a compatible vision model and enter its exact name in the app.
pause
