# Roblox Game Agent (Windows prototype)

A small, local desktop helper that observes the screen and can try short, bounded keyboard actions in Roblox. It uses ordinary keyboard input and screenshots only—no Roblox injection, exploit executor, memory reading, or anti-cheat bypass.

## Safety / scope
- Use only in your own Roblox experience, Studio test session, or a game where automation is permitted.
- Stop immediately with **F8** or the red **STOP** button.
- Autonomous mode is capped at 20 steps per run; each keypress is at most 1 second.
- The app does not browse your files. You choose one output folder; screenshots and logs are written only inside that selected folder.
- It does not read credentials, cookies, game memory, or other processes.
- Vision-based actions require a local Ollama server and a vision-capable model. Without that, you can still use Observe and manual movement controls.

## Setup
1. Install Python 3.10+ for Windows from python.org. During setup, enable **Add Python to PATH**.
2. Download this repository as a ZIP from GitHub, then extract it.
3. Open the extracted `Roblox_Game_Agent` folder.
4. Double-click `install.bat`.
5. Double-click `run.bat`.
6. Click **Choose approved output folder** and select a folder you explicitly allow the app to write to.
7. Open Roblox and join a permitted test experience. Keep the game visible.
8. Use **Observe** first. Manual movement buttons send short WASD/Space inputs.

## Optional local vision model
Install Ollama from https://ollama.com, start it, then download a vision model that Ollama supports, for example `qwen2.5vl:3b`:
```powershell
ollama pull qwen2.5vl:3b
```
In the app, enter the exact installed model name. Click **Test AI** before using **AI run (max 20 steps)**. Ollama is called only on your own computer at `http://localhost:11434`.

## Important
This is an early prototype, not a trained Roblox expert. Vision models can misunderstand the screen. Keep the game visible and be ready to stop it. Avoid use in competitive games, public experiences that prohibit automation, or anything involving purchases or trading.
