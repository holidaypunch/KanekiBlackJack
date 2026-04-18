import discord
from discord.ext import commands
import random
import os
import json
from flask import Flask
from threading import Thread
import time

app = Flask("")

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
work_cooldowns = {}
daily_cooldowns = {}

# Card deck and balance
cards = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
try:
    with open("balances.json", "r") as f:
        balances = json.load(f)
except:
    balances = {}

def save_balances():
    with open("balances.json", "w") as f:
        json.dump(balances, f)

try:
    with open("banks.json", "r") as f:
        banks = json.load(f)
except:
    banks = {}

def save_banks():
    with open("banks.json", "w") as f:
        json.dump(banks, f)

@bot.command()
async def balance(ctx, member: discord.Member = None):
    # If the user doesn't exist in balances, start them at 0
    if member is None:
        user = ctx.author.id  # get the unique ID of the user

        # If the user doesn't exist in balances, start them at 0
        if user not in balances:
            balances[user] = 0

        # Show the balance
        #await ctx.send(f"💰 {ctx.author.name}, your balance is ${balances[user]}")
        # attach image
        file = discord.File("wallet.png", filename="wallet.png")

        embed = discord.Embed(
            title="💵 Your balance",
            description=f"💰 {ctx.author.name}, your balance is ${balances[user]}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://wallet.png")

        await ctx.send(file=file, embed=embed)
    else:
        if member.id not in balances:
            balances[member.id] = 0

        # Show the balance
        # attach image
        file = discord.File("wallet.png", filename="wallet.png")

        embed = discord.Embed(
            title=f"💵 {member.name}'s balance",
            description=f"💰 {member.name}'s balance is ${balances[member.id]}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://wallet.png")

        await ctx.send(file=file, embed=embed)
    

@bot.command()
async def work(ctx, amount: int):
    user = ctx.author.id
    now = time.time()

    if user in work_cooldowns:
        last_work = work_cooldowns[user]

        if now - last_work < 300:  # 300 seconds = 5 minutes
            remaining = int(300 - (now - last_work))
            minutes = remaining // 60
            seconds = remaining % 60

            # attach image
            file = discord.File("waiting.png", filename="waiting.png")

            embed = discord.Embed(
                title="💼 Can't work now!!",
                description=f"⏳ Wait {minutes}m {seconds}s before working again.",
                color=discord.Color.gold()
            )

            embed.set_thumbnail(url="attachment://waiting.png")

            await ctx.send(file=file, embed=embed)

            #await ctx.send(f"⏳ Wait {minutes}m {seconds}s before working again.")
            return

    if amount <= 0:
        #await ctx.send("Amount must be positive.")
        
        # attach image
        file = discord.File("weary.png", filename="weary.png")

        embed = discord.Embed(
            title="💼 Invalid Work!!",
            description=f"Amount must be positive.",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://weary.png")

        await ctx.send(file=file, embed=embed)
        return

    if amount > 100000:
        #await ctx.send("The maximum amount of work cannot exceed 100000.")
        
        # attach image
        file = discord.File("weary.png", filename="weary.png")

        embed = discord.Embed(
            title="💼 Invalid Work!!",
            description=f"The maximum amount of work cannot exceed 100000.",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://weary.png")

        await ctx.send(file=file, embed=embed)
        return

    if user not in balances:
        balances[user] = 0
        save_balances()

    balances[user] += amount
    save_balances()
    work_cooldowns[user] = now

    # attach image
    file = discord.File("work.png", filename="work.png")

    embed = discord.Embed(
        title="💼 Work",
        description=f"{ctx.author.name} worked and earned ${amount}!",
        color=discord.Color.gold()
    )

    embed.add_field(name="💰 Balance", value=f"${balances[user]}", inline=False)

    embed.set_thumbnail(url="attachment://work.png")

    await ctx.send(file=file, embed=embed)

    #await ctx.send(f"💰 {ctx.author.name} worked and earned ${amount}!\nBalance: ${balances[user]}")

@bot.command()
async def daily(ctx):
    user = ctx.author.id
    now = time.time()

    if user in daily_cooldowns:
        last_daily = daily_cooldowns[user]

        if now - last_daily < 86400:
            remaining = int(86400 - (now - last_daily))
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60

            # attach image
            file = discord.File("waiting.png", filename="waiting.png")

            embed = discord.Embed(
                title="🎁 Can't claim daily now!!",
                description=f"⏳ Daily already claimed!! Wait {hours}h {minutes}m {seconds}s before claiming dailies again.",
                color=discord.Color.gold()
            )

            embed.set_thumbnail(url="attachment://waiting.png")

            await ctx.send(file=file, embed=embed)

            #await ctx.send(f"⏳ Daily already claimed!! Wait {hours}h {minutes}m {seconds}s before claiming dailies again.")
            return

    if user not in balances:
        balances[user] = 0
        save_balances()

    balances[user] += 250000
    save_balances()
    daily_cooldowns[user] = now

    # attach image
    file = discord.File("dollars.png", filename="dollars.png")

    embed = discord.Embed(
        title="🎁 Daily",
        description=f"{ctx.author.name} claimed $250000!",
        color=discord.Color.gold()
    )

    embed.add_field(name="💰 Balance", value=f"${balances[user]}", inline=False)

    embed.set_thumbnail(url="attachment://dollars.png")

    await ctx.send(file=file, embed=embed)

    #await ctx.send(f"💰 {ctx.author.name} claimed $250000!\nBalance: ${balances[user]}")

@bot.command()
async def deposit(ctx, amount: int):
    user = ctx.author.id
    
    if user not in banks:
        banks[user] = 0
        save_banks()

    if amount > balances[user]:
        await ctx.send(f"You don't have enough money to deposit!! Put valid amount.")
        return

    balances[user] -= amount
    banks[user] += amount
    save_balances()
    save_banks

    await ctx.send(f"Successfully sent ${amount} to the bank")

@bot.command()
async def withdraw(ctx, amount: int):
    user = ctx.author.id

    if user not in banks:
        banks[user] = 0
        save_banks()

    if amount > banks[user]:
        await ctx.send(f"You don't have enough money to withdraw!! Put valid amount.")
        return

    balances[user] += amount
    banks[user] -= amount
    save_balances()
    save_banks()

    await ctx.send(f"Successfully withdrew ${amount} from the bank")

@bot.command()
async def bank(ctx):
    user = ctx.author.id  # get the unique ID of the user

    # If the user doesn't exist in banks, start them at 0
    if user not in banks:
        banks[user] = 0

    # Show the bank
    await ctx.send(f"💰 {ctx.author.name}, your bank balance is ${banks[user]}")

@bot.command()
async def rob(ctx, member: discord.Member, amount: int):
    user = ctx.author.id
    victim = member.id

    # prevent self rob
    if user == victim:
        #await ctx.send("You can't rob yourself 💀")
        # attach image
        file = discord.File("cop.png", filename="cop.png")

        embed = discord.Embed(
            title="🚔 Robbing Failed!!",
            description="You can't rob yourself 💀",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://cop.png")

        await ctx.send(file=file, embed=embed)
        return

    if user not in balances:
        balances[user] = 0
    if victim not in balances:
        balances[victim] = 0

    if amount > balances[victim]:
        #await ctx.send("This person does not have enough money to rob 😢")
        # attach image
        file = discord.File("weary.png", filename="weary.png")

        embed = discord.Embed(
            title="🚔 Robbing Failed!!",
            description="This person does not have enough money to rob 😢",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://weary.png")

        await ctx.send(file=file, embed=embed)
        return

    balances[user] += amount
    balances[victim] -= amount
    save_balances()

    # attach image
    file = discord.File("yoink.png", filename="yoink.png")

    embed = discord.Embed(
        title="🥷 Robbed Successfully",
        description=f"🤑 You robbed ${amount} from {member.name}!",
        color=discord.Color.gold()
    )

    embed.add_field(name="💰 Balance", value=f"${balances[user]}", inline=False)

    embed.set_thumbnail(url="attachment://yoink.png")

    await ctx.send(file=file, embed=embed)

    #await ctx.send(f"🤑 You robbed ${amount} from {member.name}!")

@bot.command()
async def donate(ctx, member: discord.Member, amount: int):
    user = ctx.author.id
    victim = member.id

    # prevent self donate
    if user == victim:
        #await ctx.send("You can't donate to yourself 💀")
        # attach image
        file = discord.File("cop.png", filename="cop.png")

        embed = discord.Embed(
            title="🚔 Donating Failed!!",
            description="You can't donate to yourself 💀",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://cop.png")

        await ctx.send(file=file, embed=embed)
        return

    if user not in balances:
        balances[user] = 0
    if victim not in balances:
        balances[victim] = 0

    if amount > balances[user]:
        #await ctx.send("You don't have enough money to donate 😢")
        # attach image
        file = discord.File("weary.png", filename="weary.png")

        embed = discord.Embed(
            title="🚔 Donating Failed!!",
            description="You don't have enough money to donate 😢",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="attachment://weary.png")

        await ctx.send(file=file, embed=embed)
        return

    balances[user] -= amount
    balances[victim] += amount
    save_balances()

    # attach image
    file = discord.File("dollars.png", filename="dollars.png")

    embed = discord.Embed(
        title="💸 Donated Successfully",
        description=f"❤️ You donated ${amount} to {member.name}!",
        color=discord.Color.gold()
    )

    embed.add_field(name="💰 Balance", value=f"${balances[user]}", inline=False)

    embed.set_thumbnail(url="attachment://dollars.png")

    await ctx.send(file=file, embed=embed)

    #await ctx.send(f"❤️ You donated ${amount} to {member.name}!")

def draw_card():
    return random.choice(cards)

def card_value(card):
    if card in ["J","Q","K"]:
        return 10
    if card == "A":
        return 11
    return int(card)

def total(hand):
    t = sum(card_value(c) for c in hand)
    aces = hand.count("A")

    while t > 21 and aces:
        t -= 10
        aces -= 1
    return t

def format_hand(hand):
    return " ".join(hand)

class BlackjackView(discord.ui.View):
    def __init__(self, player, dealer, user_id, bet):
        super().__init__(timeout=60)
        self.player = player
        self.dealer = dealer
        self.user_id = user_id  # Track the player
        self.bet = bet          # Track their bet

    async def update(self, interaction, message):
        embed = discord.Embed(title="🃏 Blackjack")

        embed.add_field(
            name="Dealer",
            value=f"{self.dealer[0]} ?",
            inline=False
        )

        embed.add_field(
            name="You",
            value=f"{format_hand(self.player)} (Total {total(self.player)})",
            inline=False
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Ensure only the player who started the game can click
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        self.player.append(draw_card())

        if total(self.player) > 21:
            # Player busts → lose bet
            embed = discord.Embed(title="💥 Bust! You lose.")
            embed.add_field(name="Your hand", value=format_hand(self.player))
            
            # Update balance
            await interaction.response.edit_message(embed=embed, view=None)
            return

        await self.update(interaction, interaction.message)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return

        while total(self.dealer) < 17:
            self.dealer.append(draw_card())

        player_total = total(self.player)
        dealer_total = total(self.dealer)

        if dealer_total > 21 or player_total > dealer_total:
            result = f"🎉 You win! You earned ${self.bet*2}!"
            balances[self.user_id] += self.bet * 2
            save_balances()
        elif player_total == dealer_total:
            result = f"🤝 Tie! You keep your bet of ${self.bet}."
            balances[self.user_id] += self.bet
            save_balances()
        else:
            result = f"😢 Dealer wins! You lost ${self.bet}."

        embed = discord.Embed(title=result)
        embed.add_field(name="Dealer", value=f"{format_hand(self.dealer)} ({dealer_total})", inline=False)
        embed.add_field(name="You", value=f"{format_hand(self.player)} ({player_total})", inline=False)
        embed.set_footer(text=f"Balance: ${balances[self.user_id]}")

        await interaction.response.edit_message(embed=embed, view=None)

@bot.command()
async def blackjack(ctx, bet: int):
    user = ctx.author.id
    if user not in balances:
        balances[user] = 0  # starting money
        save_balances()

    if bet <= 0:
        await ctx.send("Bet must be positive.")
        return

    if bet > balances[user]:
        await ctx.send("You don't have enough money.")
        return

    balances[user] -= bet
    save_balances()

    player = [draw_card(), draw_card()]
    dealer = [draw_card(), draw_card()]

    embed = discord.Embed(title="🃏 Blackjack")
    embed.add_field(name="Dealer", value=f"{dealer[0]} ?", inline=False)
    embed.add_field(name="You", value=f"{format_hand(player)} ({total(player)})", inline=False)
    
    view = BlackjackView(player, dealer, user, bet)
    # attach image
    file = discord.File("dealer2.png", filename="dealer2.png")
    embed.set_thumbnail(url="attachment://dealer2.png")
    await ctx.send(file=file, embed=embed, view=view)

keep_alive()
bot.run(os.environ["TOKEN"])