from utils.embed import PermissionErrorEmbed, ErrorEmbed
import discord,time

class SchwimbleGromp():

    def __init__(self):
        import discord, os, datetime, random, json, threading
        from discord.ext import commands, tasks
        from utils import keepAlive, formatting, cooldown

        from dotenv import load_dotenv
        load_dotenv()

        self.discord = discord
        self.discord_commands = commands
        self.discord_tasks = tasks
        self.utils_keepAlive = keepAlive
        self.utils_formatting = formatting
        self.utils_cooldown = cooldown
        self.os = os
        self.datetime = datetime
        self.random = random
        self.json = json

        self.bot = self.discord_commands.Bot(command_prefix="test.", intents=self.discord.Intents.all())

        @self.bot.event
        async def on_ready():
            print('Logged in as')
            print(self.bot.user.name)
            print(self.bot.user.id)
            print('------')

        @self.bot.event
        async def on_command_error(ctx, e):
            if isinstance(e, discord.ext.commands.errors.CommandNotFound):
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"{e}").embed)

        @self.bot.command()
        async def humanizeSeconds(ctx, n): await ctx.send(self.utils_chatFormatting.humanizeSeconds(n))

        @self.bot.command()
        async def kms(ctx): await ctx.send("Father benjamin is bad")

        @self.bot.command()
        async def spam(ctx, msg, amt=69):
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="administrator").embed)
                return
            if amt > 200:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="Don't send more than 200 messages or I will extract your ligaments :)").embed)
                return
            for i in range(amt): await ctx.send(msg)

        @self.bot.command()
        async def clear(ctx, amt):
            return
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="administrator").embed)
                return
            amt = int(amt)
            if amt > 100:
                for i in range(amt // 100): ctx.channel.purge(limit=100)
                ctx.channel.purge(limit=amt % 100)
            else: await ctx.channel.purge(limit=amt)

        @self.bot.command()
        async def whois(ctx, user: discord.Member = None):
            if user == None: await ctx.send(embed=ErrorEmbed(ctx=ctx,message="Please specify a user").embed)
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
                        "*Doesn't know how to use a saw*"
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

        @self.bot.command()
        async def remindme(ctx,command):
            user=ctx.author
            guild=ctx.guild
            with open("data/reminders.json","r") as f: reminders=json.load(f)

            if command not in ["work","crime","rob","slut","beg","withdraw","deposit","send","cockfight","blackjack","slots","buy"]:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"I don't recognise that command").embed)
                return

            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, ctx.guild.id,f"commandsUntilCooldownRemaining_{command}")
            cooldownLength = self.db.getGuildSetting(ctx.guild.id,f"cooldowns_{command}")

            if commandsUntilCooldownRemaining > 0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"That command is not currently on cooldown").embed)
                return

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, ctx.guild.id,f"cooldowns_{command}")
                cooldowndiff = self.utils_cooldown.cooldownDiff(datetime.datetime.now(),self.utils_cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"That command is not currently on cooldown").embed)
                    return

            remainingtime=cooldownLength-cooldowndiff

            reminders["reminders"].append({
                "userid":user.id,
                "message":f"You reminder for {command} just went off!",
                "time":(self.datetime.datetime.now()+self.datetime.timedelta(seconds=remainingtime)).strftime("%Y-%m-%d %H:%M")
            })

        import asyncio

        remindercheckthread = threading.Thread(target=asyncio.run,args=(self.remindercheck))
        print(remindercheckthread)
        remindercheckthread.start()

        from utils.database import Database
        from cogs import Economy, Games, Shop

        self.db = Database()
        self.utils_keepAlive.keepAlive()
        token = self.os.environ.get("TOKEN")
        Economy.setup(self.bot, self.db)
        Games.setup(self.bot, self.db)
        Shop.setup(self.bot, self.db)
        self.bot.run(token)

    async def remindercheck(self):
        while True:
            print("reminder check")
            with open("data/reminder.json","r") as f: rems = self.json.loads(f)
            current=self.datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            needUpdate=False
            for rem in enumerate(rems["reminders"]):
                if rem[1]["time"]<=current:
                    user = self.bot.get_user(rem[1]["userid"])
                    dm = await user.create_dm()
                    await dm.send(rem[1]["message"])
                    rems["reminders"].remove(rem[0])
                    needUpdate=True
            if needUpdate:
                with open("data/reminder.json","w") as f: f.write(self.json.dumps(rems))
            time.sleep(30)

# discord.com/api/oauth2/authorize?client_id=1007622846404644884&permissions=8&scope=bot%20applications.commands

# or 4398046511095

SchwimbleGromp()
