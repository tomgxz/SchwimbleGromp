from utils.embed import PermissionErrorEmbed

class SchwimbleGromp():
    def __init__(self):
        import discord,os,datetime
        from discord.ext import commands,tasks
        from utils import keepAlive,formatting

        from dotenv import load_dotenv
        load_dotenv()

        self.discord=discord
        self.discord_commands=commands
        self.discord_tasks=tasks
        self.utils_keepAlive=keepAlive
        self.utils_formatting=formatting
        self.os=os
        self.datetime=datetime

        self.bot=self.discord_commands.Bot(command_prefix="..",intents=self.discord.Intents.all())

        @self.bot.event
        async def on_ready():
            print('Logged in as')
            print(self.bot.user.name)
            print(self.bot.user.id)
            print('------')

        @self.bot.command()
        async def humanizeSeconds(ctx,n):
            await ctx.send(self.utils_chatFormatting.humanizeSeconds(n))

        @self.bot.command()
        async def kms(ctx):
            await ctx.send("Father benjamin is bad")

        @self.bot.command()
        async def spam(ctx,msg,amt=69):
            return
            for i in range(amt):
                await ctx.send(msg)

        @self.bot.command()
        async def clear(ctx,amt):
            return
            if not ctx.message.author.guild_permissions.administrator:
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return
            amt=int(amt)
            if amt > 100:
                for i in range(amt//100):
                    ctx.channel.purge(limit=100)
                ctx.channel.purge(limit=amt%100)
            else:
                await ctx.channel.purge(limit=amt)
            

        from utils.database import Database
        from cogs import Economy, Games, Shop

        self.db = Database()
        self.utils_keepAlive.keepAlive()
        token = self.os.environ.get("TOKEN")
        Economy.setup(self.bot,self.db)
        Games.setup(self.bot,self.db)
        Shop.setup(self.bot,self.db)
        self.bot.run(token)

# discord.com/api/oauth2/authorize?client_id=1007622846404644884&permissions=8&scope=bot%20applications.commands

SchwimbleGromp()
