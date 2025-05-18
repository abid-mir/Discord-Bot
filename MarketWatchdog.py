# Standard Libraries
import os
import datetime
import random

# External Libraries
import yfinance as yf
import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import aiocron
from dotenv import load_dotenv

# ===============================
# Configuration and Setup
# ===============================
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

SUPPORTED_COMPANIES = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META',   # Tech
    'AMZN', 'TSLA', 'HD', 'COST',              # Consumer
    'JPM', 'BAC', 'GS', 'V', 'MA',             # Financials
    'UNH', 'JNJ', 'PFE', 'LLY',                # Healthcare
    'XOM', 'CVX', 'BP',                        # Energy
    'DIS', 'NFLX', 'CMCSA',                    # Media/Telecom
    'BA', 'CAT', 'UPS', 'FDX',                 # Industrial
    'WMT', 'TGT', 'NKE', 'SBUX',               # Retail
    'SPY', 'QQQ', 'ARKK'                       # ETFs
]

# Create images folder
if not os.path.exists("images"):
    os.makedirs("images")

# Bot Initialization
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ===============================
# Bot Events
# ===============================
# Triggered when the bot logs in
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Missing required arguments. Please use the help command for usage details.')

# ===============================
# Utility Functions
# ===============================
# To make df more readable
def generate_summary_message(company, df):
    if df.empty or df.shape[1] < 5:
        return f"No sufficient data available for {company}."

    date = df.index[0].strftime('%Y-%m-%d')
    msg = f"{company} EOD Data\n- Date: {date}\n"
    labels = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

    for i, label in enumerate(labels):
        value = df.iloc[0, i] if i < df.shape[1] else "N/A"
        msg += f"- {label}: {value}\n"
    return msg

# Creating Graph
def create_plot(df, columns, title, filename):
    df[columns].plot(linewidth=0.85)
    plt.xlabel('Datetime')
    plt.ylabel('Value')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# ===============================
# Command: !list-companies
# ===============================
@bot.command(name="list-companies", help="List supported companies for stock data.")
async def list_supported_companies(ctx):
    await ctx.send(SUPPORTED_COMPANIES)

# ===============================
# Command: !show-prev-day
# ===============================
@bot.command(name="show-prev-day", help="Show previous day's stock data.")
async def previous_day_stock(ctx, company):
    if company not in SUPPORTED_COMPANIES:
        await ctx.send(f"Stock data for {company} is not supported.")
        return

    try:
        df_summary = yf.download(company, period="2d", auto_adjust=False)
        if df_summary.empty:
            await ctx.send("No data available.")
            return

        msg = generate_summary_message(company, df_summary)

        df_intraday = yf.download(company, period="2d", interval="1m", auto_adjust=False)
        if df_intraday.empty:
            await ctx.send("No intraday data available.")
            return

        create_plot(df_intraday.iloc[:390], ['Close'], f"Previous Day Stock Prices - {company}", 'images/prev_day.png')
        await ctx.send(msg, file=discord.File('images/prev_day.png'))
        os.remove('images/prev_day.png')
    except Exception as e:
        await ctx.send(f"Error fetching data: {e}")

# ===============================
# Command: !show-latest
# ===============================
@bot.command(name="show-latest", help="Latest detailed plot of a company.")
async def daily_trade_updates(ctx, company):
    if company not in SUPPORTED_COMPANIES:
        await ctx.send(f"Stock data for {company} is not supported.")
        return

    df = yf.download(company, period="1d", interval="1m", auto_adjust=False)

    create_plot(df, ['Close'], f"Latest Close Prices - {company}", 'images/plot_close.png')
    create_plot(df, ['Open', 'High', 'Low', 'Close', 'Adj Close'], f"Latest OHLC Data - {company}", 'images/plot_ohlc.png')

    await ctx.send("Latest stock prices:", files=[
        discord.File('images/plot_close.png'),
        discord.File('images/plot_ohlc.png')
    ])

    os.remove('images/plot_close.png')
    os.remove('images/plot_ohlc.png')

# ===============================
# Command: !stock-history
# ===============================
@bot.command(name="stock-history", help="Plot historical stock prices for company(s).")
async def stock_history(ctx, *companies):
    #Check if compalies is empty or within SUPPORTED_COMPANIES
    if not companies or not set(companies).issubset(SUPPORTED_COMPANIES):
        await ctx.send("Invalid or no company names provided.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    for company in companies:
        df = yf.download(company, auto_adjust=False)
        df['Close'].plot(ax=ax, label=company, linewidth=0.85)

    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.title("Historical Stock Prices")
    plt.legend()
    plt.tight_layout()

    filename = 'images/historical.png'
    plt.savefig(filename)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

# ===============================
# Command: !stock-history-bw-dates
# ===============================
@bot.command(name="stock-history-bw-dates", help="Plot historical stock prices between dates. Format: !stock-history-bw-dates <company1> <company2> <YYYY-MM-DD> <YYYY-MM-DD>")
async def stock_history_between_dates(ctx, *args):
    if len(args) < 3:
        await ctx.send("Usage: !stock-history-bw-dates <companies> <start-date> <end-date>")
        return

    *companies, start_date, end_date = args
    if not set(companies).issubset(SUPPORTED_COMPANIES):
        await ctx.send("Invalid company names.")
        return

    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        await ctx.send("Incorrect date format. Use YYYY-MM-DD.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    for company in companies:
        df = yf.download(company, start=start_date, end=end_date, auto_adjust=False)
        df['Close'].plot(ax=ax, label=company, linewidth=0.85)

    plt.xlabel('Date')
    plt.ylabel('Close')
    plt.title(f"Stock Prices from {start_date} to {end_date}")
    plt.legend()
    plt.tight_layout()

    filename = 'images/history_bw_dates.png'
    plt.savefig(filename)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)

# ===============================
# Command: 	!create-text-channel
# ===============================
@bot.command(name="create-text-channel", help="Create a new text channel (admin only).")
@commands.has_role('admin')
async def create_text_channel(ctx, channel_name):
    guild = ctx.guild
    if not discord.utils.get(guild.channels, name=channel_name):
        await guild.create_text_channel(channel_name)
        await ctx.send(f'Channel `{channel_name}` created!')

# ===============================
# Cron Job: Daily 7:00 AM Summary
# ===============================
@aiocron.crontab('0 8 * * mon-fri')
async def send_daily_summary():
    company = random.choice(SUPPORTED_COMPANIES)
    df = yf.download(company, period="1d")
    msg = generate_summary_message(company, df)

    channel = discord.utils.get(bot.guilds[0].channels, name='general')
    if not channel:
        channel = await bot.guilds[0].create_text_channel('general')

    await channel.send(msg)
    await daily_trade_updates(channel, company)

# ===============================
# Cron Job: Hourly Updates
# ===============================
hour_counter = 0
intraday_df = None
active_company = ""

@aiocron.crontab('0 10-16 * * mon-fri')
async def hourly_stock_update():
    global hour_counter, intraday_df, active_company

    now = datetime.datetime.now()
    if now.hour == 10:
        hour_counter = 0
        active_company = random.choice(SUPPORTED_COMPANIES)
        intraday_df = yf.download(active_company, period="1d", interval="1m")

    slice_start = hour_counter * 60
    slice_end = min((hour_counter + 1) * 60, len(intraday_df))

    if intraday_df is not None:
        plot_df = intraday_df.iloc[slice_start:slice_end]
        filename = f'images/intraday_{hour_counter}.png'
        create_plot(plot_df, ['Close'], f"{active_company} {now.hour-1}:00 to {now.hour}:00", filename)

        channel = discord.utils.get(bot.guilds[0].channels, name='general')
        if not channel:
            channel = await bot.guilds[0].create_text_channel('general')

        await channel.send(file=discord.File(filename))
        os.remove(filename)

    hour_counter += 1


# ===============================
# Cron Job: Market Opening/Closing Alerts
# ===============================
# Opening Alert
@aiocron.crontab('15 9 * * mon-fri')
async def market_open_alert():
    channel = discord.utils.get(bot.guilds[0].channels, name='general')
    if not channel:
        channel = await bot.guilds[0].create_text_channel('general')
    await channel.send("The Indian stock market is now OPEN! Happy trading!")

# Closing Alert
@aiocron.crontab('30 15 * * mon-fri')
async def market_close_alert():
    channel = discord.utils.get(bot.guilds[0].channels, name='general')
    if not channel:
        channel = await bot.guilds[0].create_text_channel('general')
    await channel.send("The Indian stock market has CLOSED for the day.")


# ===============================
# Run the Bot
# ===============================
bot.run(DISCORD_TOKEN)
