import os
from dotenv import load_dotenv
from bot import bot

# Load .env file
load_dotenv()

# Get the token from the environment
token = os.getenv("DISCORD_TOKEN")

if token is None or token.strip() == "":
    raise ValueError("Bot token not found in .env")

# Start the bot
bot.run(token)
