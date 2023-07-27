from utils.embed import PermissionErrorEmbed, ErrorEmbed
import discord,time

class SchwimbleGromp():

    def __init__(self):
        import os
        self.os=os

        self.logFile="data/log/latest.log"
        self.sessionFile="data/session.txt"

        self.initLogger()

        import discord,os,datetime,random,json,threading
        from discord.ext import commands,tasks
        from utils import keepAlive,formatting,cooldown,channellogger

        from dotenv import load_dotenv
        load_dotenv()

        self.logger.info("Initialised dotenv")

        self.discord=discord
        self.discord_commands=commands
        self.discord_tasks=tasks
        self.utils_keepAlive=keepAlive
        self.utils_formatting=formatting
        self.utils_cooldown=cooldown
        self.datetime=datetime
        self.random=random
        self.json=json

        self.channellogger=channellogger.ChannelLogger()

        self.logger.info("Imports completed")

        self.appendSessionFile("datecreated",self.datetime.datetime.now())

        self.bot=self.discord_commands.Bot(command_prefix=".",intents=self.discord.Intents.all())

        self.logger.info("Created bot")

        @self.bot.event
        async def on_ready():
            self.logger.info(f"Logged in as {self.bot.user.name}, {self.bot.user.id}")

        @self.bot.event
        async def on_message(ctx):
            self.logger.info(f"MESSAGE: GUILD: \"{ctx.guild.name}\" CHANNEL: \"{ctx.channel.name}\" USER: \"{ctx.author.name}\" MESSAGE: \"{ctx.content}\"")
            self.channellogger.logmsg(ctx)
            await self.bot.process_commands(ctx)

        @self.bot.event
        async def on_command_error(ctx,e):
            if isinstance(e,discord.ext.commands.errors.CommandNotFound):
                self.logcommand(ctx)
                self.logger.info(f"COMMAND ERROR: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} {e}")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"{e}").embed)
            else: self.logger.error(e)

        @self.bot.command()
        async def humanizeSeconds(ctx,n):
            self.logcommand(ctx)
            await ctx.send(self.utils_chatFormatting.humanizeSeconds(n))

        @self.bot.command()
        async def kms(ctx):
            self.logcommand(ctx)
            await ctx.send("Father benjamin is bad")

        @self.bot.command()
        async def spam(ctx,msg,amt=69):
            self.logcommand(ctx)
            if (not ctx.message.author.guild_permissions.administrator or True) and (not ctx.message.author.id==879801241859915837) and (not ctx.message.author.id==786895386476281936):
                self.logger.info(f"COMMAND ERROR: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} Administrator permission required")
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return
            if amt > 200:
                self.logger.info(f"COMMAND ERROR: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} amount greater than 200")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="Don't send more than 200 messages or I will extract your ligaments :)").embed)
                return
            for i in range(amt): await ctx.send(msg)

        @self.bot.command()
        async def clear(ctx,amt):
            self.logcommand(ctx)
            return
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return
            amt = int(amt)
            if amt>100:
                for i in range(amt//100): ctx.channel.purge(limit=100)
                ctx.channel.purge(limit=amt%100)
            else: await ctx.channel.purge(limit=amt)

        @self.bot.command()
        async def whois(ctx,user:discord.Member=None):
            self.logcommand(ctx)
            if user==None:
                self.logger.info(f"COMMAND ERROR: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} user not specified")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="Please specify a user").embed)
            if user.id==786895386476281936:
                await ctx.send("Andrew (the one with the small peen)")
                await ctx.send("*He's actually Will*")
            if user.id==1011713928969080883:
                await ctx.send("Davinko")
                await ctx.send(
                    self.random.choice([
                        "*The one being sued for copyright infringement*",
                        "*Is addicted to vore*",
                        "*Gets turned on by silicon cupcakes*",
                        "*Has two baby pigs that answer to his summons*",
                        "*Very small and very loud*"
                    ]))
            if user.id==337662943950798866: await ctx.send("Father Bonjamon")
            if user.id==880838570208817164:
                await ctx.send("The atomic physics nerd")
                await ctx.send(
                    self.random.choice(["*Likes kids*", "*In search of mangos*"]))
            if user.id==769100736298090497:
                await ctx.send("Will's boyfriend")
            if user.id==879801241859915837: await ctx.send("Father Thomas")
            if user.id==889530180299808800:
                await ctx.send("Norris")
                await ctx.send(
                    self.random.choice([
                        "*Inhales copious amounts of dried milk*",
                        "*Drug Dealer*",
                        "*Has a secret Fantasyphet business in your basement*",
                        "*Dislikes minorities*"
                    ]))
            if user.id==1017083666796654592:
                await ctx.send("Roberto")
                await ctx.send(self.random.choice(["*Cannot lie to save his life*","*Doesn't know how to use a saw*"]))
            if user.id==922555321501749338:
                await ctx.send("Dave Jr.")
                await ctx.send(self.random.choice(["*Small*"]))
            if user.id==1007622846404644884:
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

        from utils.database import Database
        from cogs import Economy,Games,Shop

        self.logger.info("Imported databases and cogs")

        self.db=Database()
        self.utils_keepAlive.keepAlive()

        self.logger.info("Started keepAlive")

        token = self.os.environ.get("TOKEN")
        Economy.setup(self.bot,self.db,self.logger)
        Games.setup(self.bot,self.db,self.logger)
        Shop.setup(self.bot,self.db,self.logger)

        self.logger.info("Initialized cogs")

        self.bot.run(token)

    def initLogger(self):
        """Initialises the logger and resets the log file"""

        commands=[] # used to store log commands before the log has been generated, so that they can be appended

        #if not (self.os.path.exists(self.sessionFile) or self.os.path.exists(self.logFile)):
        if self.os.path.exists(self.sessionFile) and self.os.path.exists(self.logFile): # if both files exist, session.txt and latest.log
            with open(self.sessionFile,"r") as f:
                lines=f.read()
                if lines=="": # if there are no lines in the file
                    commands.append(lambda:self.logger.warning("Session file is empty"))
                    self.previousSessionData={}
                else:
                    self.previousSessionData={line.split(":")[0]:line.split(":")[1] for line in [x.strip("\n") for x in lines.split("\n")]}

            open(self.sessionFile,"w").close() # clear file

            logFileInt=1
            logFileName=None
            try: logFileName=f"data/log/{self.previousSessionData['datecreated']}-%.log"
            except KeyError as e: # no attribute found in the session data
                commands.append(lambda:self.logger.error("No date created attribute in session file - previous log file will be deleted"))
            else:
                while True:
                    if self.os.path.exists(logFileName.replace("%",str(logFileInt))): logFileInt+=1
                    else: break

                with open(self.logFile,"r") as f1:
                    with open(logFileName.replace("%",str(logFileInt)),"w") as f2:
                        f2.write(f1.read())

            open(self.logFile,"w").close() # clear file

        elif self.os.path.exists(self.sessionFile) and not(self.os.path.exists(self.logFile)): # if latest.log doesnt exist
            commands.append(lambda:self.logger.warning("Previous log file does not exist"))
            if not self.os.path.exists("data/log/"): self.os.makedirs("data/log/")
            open(self.logFile,"w").close()

        elif (not self.os.path.exists(self.sessionFile)) and (not self.os.path.exists(self.logFile)): # if neither exists
            commands.append(lambda:self.logger.warning("Previous log file does not exist"))
            commands.append(lambda:self.logger.warning("Session file does not exist"))

            # clear both files
            open(self.logFile,"w").close()
            open(self.sessionFile,"w").close()

        else: # anything else
            commands.append(lambda:self.logger.warning("Session file does not exist"))

            # clear both files
            open(self.logFile,"w").close()
            open(self.sessionFile,"w").close()

        from utils.logger import Logger
        self.logger=Logger(sessionFile=self.sessionFile,logFile=self.logFile) # generate the logger

        for command in commands: command()

        self.logger.info("Logging initialised")

    def appendSessionFile(self,key,value):
        """
        Adds an entry to the session.txt file found in the data/ directory. Entry is in the format <param key>:<param value>

        :param key str:
            The key of the entry. Will be succeeded by :param value:
        :param value str:
            The value of the entry. Will be prefixed by :param key:
        """

        self.logger.info("Appending data to session file")

        with open(self.sessionFile,"r") as f:
            old=f.read()
            f.close()

        with open(self.sessionFile,"w") as f:
            if old != "": f.write(f"{old}\n{key}:{value}")
            else: f.write(f"{key}:{value}")

        self.logger.info("Data appended to session file")

    def logcommand(self,ctx): self.logger.info(f"COMMAND: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} \"{ctx.message.content}\"")


# discord.com/api/oauth2/authorize?client_id=1007622846404644884&permissions=8&scope=bot%20applications.commands
# or 4398046511095

SchwimbleGromp()
