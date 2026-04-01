import discord
from discord.ext import commands
import random
import os
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.command()
async def balance(ctx):
    user = ctx.author.id  # get the unique ID of the user

    # If the user doesn't exist in balances, start them at 0
    if user not in balances:
        balances[user] = 0

    # Show the balance
    await ctx.send(f"💰 {ctx.author.name}, your balance is ${balances[user]}")

@bot.command()
async def work(ctx, amount: int):

    user = ctx.author.id

    if amount <= 0:
        await ctx.send("Amount must be positive.")
        return

    if user not in balances:
        balances[user] = 0
        save_balances()

    balances[user] += amount
    save_balances()

    await ctx.send(f"💰 {ctx.author.name} worked and earned ${amount}!\nBalance: ${balances[user]}")

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
            value=f"{format_hand(self.dealer)} (Total {total(self.dealer)})",
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
    await ctx.send(embed=embed, view=view)

bot.run(os.environ["TOKEN"])