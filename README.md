#Sports Bot API Project

This project connects a FastAPI backend with a Discord bot to manage and display sports data.

##Features
- Add and view teams
- Add and view games
- Live score lookup using external sports API
- Discord bot commands for interaction

##How to Run

###Start API
```bash
cd API_Handling
python -m uvicorn main:app --reload

### Start Bot
cd DiscordBot_Integration
python bot.py
