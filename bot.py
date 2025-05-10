import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime

GUILD_ID = 1370498801017815151  # Replace with your server ID
STAFF_ROLE_ID = 1370504397267927110  # Staff role ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

conn = sqlite3.connect("hifly.db")
cursor = conn.cursor()

# Ensure tables exist
cursor.execute("""CREATE TABLE IF NOT EXISTS flights (
    code TEXT PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    departure_time TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    flight_code TEXT,
    image_url TEXT,
    timestamp TEXT,
    reason TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS ranks (
    user_id INTEGER PRIMARY KEY,
    rank TEXT
)""")

conn.commit()

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Logged in as {bot.user} and synced commands.")

def is_staff(interaction: discord.Interaction):
    return any(role.id >= STAFF_ROLE_ID for role in interaction.user.roles)

@bot.tree.command(name="create_flight", description="Create a new flight", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(code="Flight code", origin="Origin", destination="Destination", departure_time="Departure time")
async def create_flight(interaction: discord.Interaction, code: str, origin: str, destination: str, departure_time: str):
    if not is_staff(interaction):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    cursor.execute("INSERT INTO flights (code, origin, destination, departure_time) VALUES (?, ?, ?, ?)",
                   (code.upper(), origin, destination, departure_time))
    conn.commit()
    await interaction.response.send_message(f"Flight `{code.upper()}` created.")

@bot.tree.command(name="flights", description="List all active flights", guild=discord.Object(id=GUILD_ID))
async def flights(interaction: discord.Interaction):
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    if not flights:
        await interaction.response.send_message("No flights available.")
        return
    msg = "**Active Flights:**\n"
    for f in flights:
        msg += f"`{f[0]}`: {f[1]} -> {f[2]} at {f[3]}\n"
    await interaction.response.send_message(msg)

@bot.tree.command(name="flight_log", description="Log a flight", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(flight_code="Flight code", image_url="Image URL (proof)")
async def flight_log(interaction: discord.Interaction, flight_code: str, image_url: str):
    cursor.execute("INSERT INTO logs (user_id, flight_code, image_url, timestamp, reason) VALUES (?, ?, ?, ?, ?)",
                   (interaction.user.id, flight_code.upper(), image_url, datetime.utcnow().isoformat(), ""))
    conn.commit()
    await interaction.response.send_message("Flight logged!")

@bot.tree.command(name="my_logs", description="View your own flight logs", guild=discord.Object(id=GUILD_ID))
async def my_logs(interaction: discord.Interaction):
    cursor.execute("SELECT flight_code, timestamp FROM logs WHERE user_id=?", (interaction.user.id,))
    logs = cursor.fetchall()
    if not logs:
        await interaction.response.send_message("No logs found.")
        return
    msg = "**Your Flight Logs:**\n"
    for log in logs:
        msg += f"{log[0]} at {log[1]}\n"
    await interaction.response.send_message(msg)

bot.run("MTM3MDcwMDU2MTk4MDA2NzkwMA.Gs6mZa.0ZOwo98CFhD0-iszAt2v3LdKn3gkTghZEraFvA")
