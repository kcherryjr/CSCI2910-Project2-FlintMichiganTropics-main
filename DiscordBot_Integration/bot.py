import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
import sys
import asyncio

# 👇 THIS FIXES IMPORT ISSUE
sys.path.append(os.path.abspath("../API_Handling"))

from liveapi import LiveScores

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ------------------------
# BASIC COMMANDS
# ------------------------

@bot.command()
async def ping(ctx):
    await ctx.send("Bot is working!")


@bot.command()
async def teams(ctx):
    try:
        response = requests.get("http://127.0.0.1:8000/teams")
        data = response.json()

        if not data:
            await ctx.send("No teams found.")
            return

        message = "Teams:\n"
        for team in data:
            message += f"- {team['name']} ({team['sport']})\n"

        await ctx.send(message)

    except Exception as e:
        await ctx.send("Error connecting to API.")
        print(e)


@bot.command()
async def addteam(ctx, name: str, sport: str):
    try:
        payload = {"name": name, "sport": sport}
        response = requests.post("http://127.0.0.1:8000/teams", json=payload)

        if response.status_code == 200:
            await ctx.send(f"Added team: {name}")
        else:
            await ctx.send("Failed to add team.")

    except Exception as e:
        await ctx.send("Error connecting to API.")
        print(e)


@bot.command()
async def addgame(ctx, home_team_id: int, away_team_id: int, home_score: int, away_score: int):
    try:
        payload = {
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score
        }

        response = requests.post("http://127.0.0.1:8000/games", json=payload)

        if response.ok:
            await ctx.send("Game added successfully!")
        else:
            await ctx.send(f"Failed to add game. Status: {response.status_code}")

    except Exception as e:
        await ctx.send("Error connecting to API.")
        print(e)


@bot.command()
async def games(ctx):
    try:
        teams_res = requests.get("http://127.0.0.1:8000/teams")
        teams = teams_res.json()
        team_map = {team["id"]: team["name"] for team in teams}

        response = requests.get("http://127.0.0.1:8000/games")
        data = response.json()

        if not data:
            await ctx.send("No games found.")
            return

        message = "Games:\n"
        for game in data:
            home = team_map.get(game["home_team_id"], "Unknown")
            away = team_map.get(game["away_team_id"], "Unknown")

            message += f"{home} vs {away} | {game['home_score']}-{game['away_score']}\n"

        await ctx.send(message)

    except Exception as e:
        await ctx.send("Error connecting to API.")
        print(e)


# ------------------------
# LIVE SCORE COMMAND
# ------------------------

@bot.command()
async def live(ctx, sport, *, team):
    try:
        live = LiveScores(sport, team)
        result = live.get_team()

        if not result:
            await ctx.send("⚠️ No data available.")
            return

        if result["status"] != "live":
            await ctx.send("❌ No live game found.")
            return

        await ctx.send(
            f"🔥 LIVE GAME:\n"
            f"{result['home']} vs {result['away']}\n"
            f"Score: {result['home_score']}-{result['away_score']}"
        )

    except Exception as e:
        await ctx.send("Error fetching live score.")
        print(e)


# ------------------------
# WATCH (AUTO-UPDATES)
# ------------------------

@bot.command()
async def watch(ctx, sport, *, team):
    await ctx.send(f"👀 Watching {team}...")

    last_score = None

    for _ in range(10):
        try:
            live = LiveScores(sport, team)
            result = live.get_team()

            if not result or result["status"] != "live":
                await ctx.send(f"❌ No live game for {team}")
                return

            score = f"{result['home_score']}-{result['away_score']}"

            if score != last_score:
                await ctx.send(
                    f"🔥 LIVE UPDATE:\n"
                    f"{result['home']} vs {result['away']}\n"
                    f"Score: {score}"
                )
                last_score = score

        except Exception as e:
            await ctx.send("Error getting live data.")
            print(e)
            return

        await asyncio.sleep(30)

    await ctx.send(f"⏹️ Done watching {team}.")


bot.run(TOKEN)