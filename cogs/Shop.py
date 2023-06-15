from discord.ext import commands
from utils.embed import Embed, EmbedType, WalletAmountInsufficientEmbed, ErrorEmbed
from utils.other import wrapQuotes,csvToList,listToCsv,removeAll
from utils import items,cooldown
from utils import formatting as humanize
import pickle, json, datetime

class Shop(commands.Cog):
    def __init__(self,bot,database,logger):
        self.bot=bot
        self.db=database
        self.logger=logger

        with open("data/defaultGuildSettings.json", "r") as f:
            self.defaultGuildSettings = json.load(f)
        with open("data/defaultUserSettings.json", "r") as f:
            self.defaultUserSettings = json.load(f)

    # UTILS

    async def newWalletBalance(self,ctx):
        await ctx.send(embed=Embed(ctx=ctx,message=f"Your new wallet balance is {humanize.humanizeNumber(self.db.getUserBalances(ctx.author.id,ctx.guild.id)[0])} {self.db.getGuildSetting(ctx.guild.id,'coinname')}").embed)

    async def newBankBalance(self,ctx):
        await ctx.send(embed=Embed(ctx=ctx,message=f"Your new bank balance is {humanize.humanizeNumber(self.db.getUserBalances(ctx.author.id,ctx.guild.id)[1])}").embed)

    async def openAccount(self,user,guildid):
        if user.id not in self.db.getDiscordUserList(guildid): self.db.addUser(user.id,guildid,self.defaultUserSettings)

    def logcommand(self,ctx): self.logger.info(f"COMMAND: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} \"{ctx.message.content}\"")

    # COMMANDS

    @commands.command()
    async def buy(self,ctx,item=None):
        """Purchase an item of your choice, if you have the funds
        Arguments: item, required, the item that you want to buy
        Permission required: None
        Aliases: None"""

        async with ctx.typing():
            coinname=self.db.getGuildSetting(ctx.guild.id,"coinname")
            user=ctx.author
            guild=ctx.guild
            await self.openAccount(user,guild.id)

            # COOLDOWN HANDLING

            cooldownCommand = "buy"
            commandsUntilCooldown = self.db.getGuildSetting(guild.id,f"commandsUntilCooldown_{cooldownCommand}")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id,guild.id,f"commandsUntilCooldownRemaining_{cooldownCommand}")
            firstCommandExecuted = self.db.getUserSetting(user.id,guild.id,f"firstCommandExecuted_{cooldownCommand}")
            cooldownLength=self.db.getGuildSetting(guild.id,f"cooldowns_{cooldownCommand}")

            if commandsUntilCooldownRemaining == 0: # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id,guild.id,f"cooldowns_{cooldownCommand}")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength: # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id,guild.id,f"commandsUntilCooldownRemaining_{cooldownCommand}",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id,guild.id,f"firstCommandExecuted_{cooldownCommand}",'""')

                else: # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"buy an item",remainingTime=cooldownLength-cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id,f"commandsUntilCooldownResetTime"): # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id,guild.id,f"commandsUntilCooldownRemaining_{cooldownCommand}",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown: # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id,guild.id,f"firstCommandExecuted_{cooldownCommand}",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(user.id,guild.id,f"cooldowns_{cooldownCommand}",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            bal=self.db.getUserBalances(user.id,guild.id)[0]

            if item==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="You did not specify an item").embed)
                return

            item = item.lower()

            if item not in csvToList(self.db.getGuildSetting(guild.id,"shop_availableItems")):
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="That item is not being sold in the shop right now").embed)
                return

            itemprice = self.db.getGuildSetting(guild.id,f"shop_{item}_price")

            if itemprice > bal:
                await ctx.send(embed=WalletAmountInsufficientEmbed(ctx=ctx,coinname=coinname).embed)
                return

            useritems = removeAll(csvToList(self.db.getUserSetting(user.id,guild.id,f"inventory_{item}")),""," ")

            if len(useritems) >= self.db.getGuildSetting(guild.id,f"shop_{item}_max"):
                message=f"You can't buy any more {item}s"
                if item == "chicken": message = f"{message} - send one to fight!"
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=message).embed)
                return

            if item == "chicken":
                useritems.append(str(pickle.dumps(items.newChicken())))
                self.db.setUserSetting(user.id,guild.id,f"inventory_{item}",listToCsv(useritems))
                await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message="You have bought a chicken to fight with!").embed)
            else: await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message="Purchase successful!").embed)

            await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id,guild.id,f"commandsUntilCooldownRemaining_{cooldownCommand}")
        if commandsUntilCooldownRemaining > 0: # decrease cooldown value by 1
            self.db.setUserSetting(user.id,guild.id,f"commandsUntilCooldownRemaining_{cooldownCommand}",wrapQuotes(commandsUntilCooldownRemaining-1))

    @commands.command(aliases=["inv"])
    async def inventory(self,ctx):
        """View the items you have purchased
        Arguments: None
        Permission required: None
        Aliases: inv"""

        async with ctx.typing():
            coinname=self.db.getGuildSetting(ctx.guild.id,"coinname")
            user=ctx.author
            guild=ctx.guild
            await self.openAccount(user,guild.id)

            f=[]

            for item in csvToList(self.db.getGuildSetting(guild.id,"shop_availableItems")):
                print()
                f.append([f"{item.title()}s",f"You own {humanize.humanizeNumber(len(removeAll(csvToList(self.db.getUserSetting(user.id,guild.id,f'inventory_{item}')),'')))}"])

        await ctx.send(embed=Embed(ctx=ctx,message="**Inventory**",fields=f,inline=True).embed)

    @commands.command()
    async def price(self,ctx,item=None):
        """See how much an item costs
        Arguments: None
        Permission required: None
        Aliases: inv"""

        async with ctx.typing():
            coinname=self.db.getGuildSetting(ctx.guild.id,"coinname")
            user=ctx.author
            guild=ctx.guild
            await self.openAccount(user,guild.id)

            if item == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="You need to specify an item").embed)
                return

            item = item.lower()

            if item not in csvToList(self.db.getGuildSetting(guild.id,"shop_availableItems")):
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message="That item is not being sold in the shop right now").embed)
                return

        await ctx.send(embed=Embed(ctx=ctx,message=f"One {item} costs {self.db.getGuildSetting(guild.id,f'shop_{item}_price')} {coinname}").embed)


def setup(bot,database,logger): bot.add_cog(Shop(bot,database,logger))
