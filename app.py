import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Intents and bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")
    await bot.process_commands(message)

@bot.command(name="solve")
async def solve(ctx, language: str, *, problem_description: str):
    """
    Command to solve a LeetCode problem.
    Usage: !solve <language> <problem_description>
    """
    await ctx.send(f"Processing your request to solve the problem in `{language}`. Please wait...")

    # Generate solution using GPT-4
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert programmer skilled in solving algorithmic problems."},
                {
                    "role": "user",
                    "content": (
                        f"Write a solution for the following LeetCode problem in {language}:\n\n"
                        f"{problem_description}\n\n"
                        "Include only the code and a detailed explanation of the solution."
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=1500,  # Set a limit on the response length
        )

        # Extract response
        solution = response.choices[0].message.content.strip()

        # Split solution if too long
        if len(solution) > 2000:
            await ctx.send("The solution is too long to send in one message. Sending in parts...")
            parts = [solution[i:i + 2000] for i in range(0, len(solution), 2000)]
            for part in parts:
                await ctx.send(part)
        else:
            await ctx.send(solution)

    except Exception as e:
        await ctx.send(f"An error occurred while solving the problem: {e}")

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
