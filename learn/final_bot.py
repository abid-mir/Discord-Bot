# Standard libraries
import os
import datetime
import random

# External libraries for stock data and plotting
import yfinance as yf
import plotly.express as px
import matplotlib.pyplot as plt

# Load environment variables from .env file
from dotenv import load_dotenv

# Discord API
import discord
from discord.ext import commands

# Scheduled tasks (cron jobs)
import aiocron

# Import custom functionality (assumed to contain plot generation methods)
import final_sub_bot

# List of top stock symbols the bot will support
top_stock_companies = [
    'AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'FB', 'BRK-B', 'SPY',
    'BABA', 'JPM', 'WMT', 'V', 'T', 'UNH', 'PFE', 'INTC', 'VZ', 'ORCL'
]

# Global variables for managing cron-based tasks
df = None
df_not_none = False
count = 0
random_company = ''
nrows = 0

# Create directory to store images if it doesn't exist
if not os.path.exists("images"):
    os.mkdir("images")

# Load environment variable for Discord bot token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up bot with command prefix '!' and intent to read message content
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Triggered when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# List available stock companies
@bot.command(name="get-list", help="Check list of companies for which stock details can be fetched.")
async def get_list(ctx):
    await ctx.send(top_stock_companies)

# Fetch and send previous day's stock data of a specified company
@bot.command(name="prev-stock-data", help="Check previous day stock data of a company.")
async def stock_data(ctx, stock_company):
    if stock_company in top_stock_companies:
        try:
            # Fetch previous day summary
            stock_company_df = yf.download(stock_company, period="2d", auto_adjust=False)
            if stock_company_df.empty:
                await ctx.send("No data available.")
                return

            msg = create_msg(stock_company, stock_company_df)
            print("Message created")

            # Fetch 1-minute interval data
            stock_company_df = yf.download(stock_company, period="2d", interval="1m", auto_adjust=False)
            if stock_company_df.empty:
                await ctx.send("No intraday data available.")
                return
            print("Intraday data fetched")

            stock_company_df[0:390].plot(y='Close', linewidth=0.85)
            plt.xlabel('Datetime')
            plt.ylabel('Close')
            plt.title(f"Stock prices of {stock_company} for previous day")

            plt.savefig('images/stock_previous_day.png')
            print("Plot saved")

            await ctx.send(msg, file=discord.File('images/stock_previous_day.png'))
            print("Sent to Discord")

            os.remove('images/stock_previous_day.png')
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    else:
        await ctx.send(f"Stock data for {stock_company} doesn't exist!")
        

# Utility function to format EOD stock data message
def create_msg(top_stock_company, df):
    # Defensive programming: check for minimum rows/columns
    if df.empty or df.shape[0] < 1 or df.shape[1] < 5:
        return f"No sufficient data available for {top_stock_company}."

    date = str(df.index[0]).split(' ')[0]
    col_names = df.columns.tolist()

    msg = f"{top_stock_company} EOD Data\n"
    msg += f"- Date: {date}\n"

    # Map expected labels to columns, if they exist
    field_labels = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    for i, label in enumerate(field_labels):
        value = df.iloc[0, i] if i < df.shape[1] else "N/A"
        msg += f"- {label}: {value}\n"

    return msg


# Show latest detailed 1-day plot of a company using helper module
@bot.command(name="daily-trade-updates", help="Check latest detailed plot of a company.")
async def get_daily_trade_updates_plot(ctx, stock_company):
    if stock_company in top_stock_companies:
        await final_sub_bot.send_daily_trade_updates_plot(stock_company, ctx)
    else:
        await ctx.send(f"Stock data plot for {stock_company} doesn't exist!")

# Show historical data plots of multiple companies
@bot.command(name="stock-history", help="Check historical plot of a company(s).")
async def get_stock_history(ctx, *args):
    if len(args) >= 1:
        if set(args).issubset(tuple(top_stock_companies)):
            await final_sub_bot.send_history_plot(args, ctx)
        else:
            await ctx.send("Invalid set of companies!")
    else:
        await ctx.send("Please enter at least one company as argument.")

# Show historical data plots for specific date ranges
@bot.command(name="stock-history-bw-dates", help="Check historical plot of company(s) for start & end date.")
async def get_stock_history_in_date_interval(ctx, *args):
    if len(args) >= 3:
        await final_sub_bot.send_history_plot_in_date_interval(args, ctx)
    else:
        await ctx.send("Please enter correct usage")

# Command restricted to 'admin' role for creating channels
@bot.command(name="create-channel", help="An admin creates a new channel.")
@commands.has_role('admin')
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if not existing_channel:
        print(f'Creating a new channel- {channel_name}...')
        await guild.create_text_channel(channel_name)
        print('Channel created!')

# Handle errors for commands (e.g. missing arguments, wrong roles)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Please enter correct usage.')




# CRON: Send daily morning stock data to a Discord channel at 7:00 AM Mon–Fri
@aiocron.crontab('0 7 * * mon-fri')
async def send_stock_details():
    top_stock_company = random.choice(top_stock_companies)
    top_stock_company_df = yf.download(top_stock_company, period="1d")

    msg = create_msg(top_stock_company, top_stock_company_df)

    existing_channel = discord.utils.get(bot.guilds[0].channels, name='stock-details')

    # Create channel if it doesn't exist
    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(bot.guilds[0].channels, name='stock-details')

    # Send message and plot
    await existing_channel.send(msg)
    await final_sub_bot.send_daily_trade_updates_plot(top_stock_company, existing_channel)

# CRON: Send hourly stock updates between 10:30 AM and 4:30 PM Mon–Fri
@aiocron.crontab('30 10-16 * * mon-fri')
async def show_hourly_plot():
    global df_not_none, count, df, random_company, nrows

    now = datetime.datetime.now()

    if now.hour == 10:
        # Initialize data for first hour
        df_not_none = True
        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company, period="1d", interval="1m")
        nrows = len(df.index)
    elif not df_not_none:
        # Determine which hour this is (used for slicing)
        df_not_none = True
        count = max(1, min(now.hour - 10 + 1, 6))

        random_company = random.choice(top_stock_companies)
        df = yf.download(random_company, period="1d", interval="1m")
        nrows = len(df.index)

    # Set slice limit (60 minutes per hour)
    limiter = 6.5 if count == 6 else (count + 1)
    slice_limiter = 60 * limiter
    if count == 6 and nrows != 390:
        slice_limiter = nrows  # Adjust if incomplete day

    # Generate and save plot
    df[60 * count: slice_limiter].plot(y='Close', linewidth=0.85)
    plt.xlabel('Datetime')
    plt.ylabel('Close')
    plt.title(f'Stock prices of {random_company} for {now.hour-1}:30 - {now.hour}:30')
    plt.savefig(f'images/stock_{count}.png')

    # Get channel or create it if missing
    existing_channel = discord.utils.get(bot.guilds[0].channels, name='stock-details')
    if not existing_channel:
        print(f'Creating a new channel- stock-details...')
        await bot.guilds[0].create_text_channel("stock-details")
        print('Channel created!')
        existing_channel = discord.utils.get(bot.guilds[0].channels, name='stock-details')

    # Send image and clean up
    await existing_channel.send(file=discord.File(f'images/stock_{count}.png'))
    os.remove(f'images/stock_{count}.png')

    # Update count for next hour
    count += 1

    # Reset after 4 PM
    if now.hour == 16:
        df_not_none = False
        count = 0

# Start bot
bot.run(TOKEN)
