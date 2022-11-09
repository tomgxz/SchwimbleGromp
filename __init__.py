from utils.embed import PermissionErrorEmbed
import discord


class SchwimbleGromp():

    def __init__(self):
        import discord, os, datetime, random
        from discord.ext import commands, tasks
        from utils import keepAlive, formatting

        from dotenv import load_dotenv
        load_dotenv()

        self.discord = discord
        self.discord_commands = commands
        self.discord_tasks = tasks
        self.utils_keepAlive = keepAlive
        self.utils_formatting = formatting
        self.os = os
        self.datetime = datetime
        self.random = random

        self.bot = self.discord_commands.Bot(
            command_prefix="..", intents=self.discord.Intents.all())

        @self.bot.event
        async def on_ready():
            print('Logged in as')
            print(self.bot.user.name)
            print(self.bot.user.id)
            print('------')

        @self.bot.command()
        async def humanizeSeconds(ctx, n):
            await ctx.send(self.utils_chatFormatting.humanizeSeconds(n))

        @self.bot.command()
        async def kms(ctx):
            await ctx.send("Father benjamin is bad")

        @self.bot.command()
        async def spam(ctx, msg, amt=69):
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(
                    ctx=ctx, permission="administrator").embed)
                return
            if amt > 200:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="Don't send more than 200 messages or I will extract your ligaments :)").embed)
            for i in range(amt):
                await ctx.send(msg)

        @self.bot.command()
        async def clear(ctx, amt):
            return
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(
                    ctx=ctx, permission="administrator").embed)
                return
            amt = int(amt)
            if amt > 100:
                for i in range(amt // 100):
                    ctx.channel.purge(limit=100)
                ctx.channel.purge(limit=amt % 100)
            else:
                await ctx.channel.purge(limit=amt)

<<<<<<< Updated upstream
        @self.bot.command()
        async def whois(ctx, user: discord.Member = None):
            if user == None: await ctx.send("You forgot to specify a user")
            if user.id == 786895386476281936:
                await ctx.send("Andrew (the one with the small peen)")
                await ctx.send("*He's actually Will*")
            if user.id == 1011713928969080883:
                await ctx.send("Davinko")
                await ctx.send(
                    self.random.choice([
                        "*The one being sued for copyright infringement*",
                        "*Is addicted to vore*",
                        "*Gets turned on by silicon cupcakes*",
                        "*Has two baby pigs that answer to his summons*",
                        "*Very small and very loud*"
                    ]))
            if user.id == 337662943950798866: await ctx.send("Father Bonjamon")
            if user.id == 880838570208817164:
                await ctx.send("The atomic physics nerd")
                await ctx.send(
                    self.random.choice(
                        ["*Likes kids*", "*In search of mangos*"]))
            if user.id == 769100736298090497:
                await ctx.send("Will's boyfriend")
            if user.id == 879801241859915837: await ctx.send("Father Thomas")
            if user.id == 889530180299808800:
                await ctx.send("Norris")
                await ctx.send(
                    self.random.choice([
                        "*Inhales copious amounts of dried milk*",
                        "*Drug Dealer*",
                        "*Has a secret Fantasyphet business in your basement*",
                        "*Dislikes minorities*"
                    ]))
            if user.id == 1017083666796654592:
                await ctx.send("Roberto")
                await ctx.send(
                    self.random.choice([
                        "*Cannot lie to save his life*",
                    ]))
            if user.id == 922555321501749338:
                await ctx.send("Dave Jr.")
                await ctx.send(self.random.choice([
                    "*Small*",
                ]))
            if user.id == 1007622846404644884:
                await ctx.send("Schwimble Gromp")
                await ctx.send(
                    self.random.choice([
                        "*his family tree is a recycling symbol*",
                        "*he is the apex homosexcual*",
                        "*won 1st place in the Bahjhongha race*",
                        "*has a large supply of silicon cupcakes*",
                        "*has a sex hole*",
                        "*he constipates life incessantly*",
                        "*wields a 10ft schlong that he got from ikea*",
                        "*is 1ft tall*",
                        "*has an entire lego collection made about him*",
                        "*heavy fantasyphet addict*"
                    ]))
=======
>>>>>>> Stashed changes

        from utils.database import Database
        from cogs import Economy, Games, Shop

        self.db = Database()
        self.utils_keepAlive.keepAlive()
        token = self.os.environ.get("TOKEN")
        Economy.setup(self.bot, self.db)
        Games.setup(self.bot, self.db)
        Shop.setup(self.bot, self.db)
        self.bot.run(token)


# discord.com/api/oauth2/authorize?client_id=1007622846404644884&permissions=8&scope=bot%20applications.commands

# or 4398046511095

SchwimbleGromp()
