import discord,random,json,datetime
from discord.ext import commands
from utils import replies,cooldown
from utils import formatting as humanize
from utils.embed import Embed,EmbedType,ErrorEmbed,PermissionErrorEmbed,BankAmountInsufficientEmbed,WalletAmountInsufficientEmbed,InvalidIntEmbed,CooldownEmbed
from utils.other import wrapQuotes
from utils.assets import strings


class Economy(commands.Cog):

    def __init__(self,bot,database,logger):
        self.bot=bot
        self.db=database
        self.logger=logger

        self.logger.info("Loading Economy cog")

        #from utils.logger import Logger
        #self.logger=Logger(sessionFile="data/session.txt",logFile="data/log/latest.log" ) # generate the logger

        with open("data/defaultGuildSettings.json", "r") as f: self.defaultGuildSettings = json.load(f)
        with open("data/defaultUserSettings.json", "r") as f: self.defaultUserSettings = json.load(f)

    # UTILS

    # self.logger.info(f"COMMAND ERROR: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} user not specified")

    async def newWalletBalance(self,ctx):
        bal=self.db.getUserBalances(ctx.author.id,ctx.guild.id)[0]
        self.logger.info(f"New Wallet Balance: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} {bal}")
        await ctx.send(embed=Embed(ctx=ctx,message=strings.NEW_WALLET_BALANCE % (humanize.humanizeNumber(bal),self.db.getGuildSetting(ctx.guild.id,'coinname'))).embed)

    async def newBankBalance(self,ctx):
        bal=self.db.getUserBalances(ctx.author.id,ctx.guild.id)[1]
        self.logger.info(f"New Bank Balance: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} {bal}")
        await ctx.send(embed=Embed(ctx=ctx,message=strings.NEW_BANK_BALANCE % (humanize.humanizeNumber(bal),self.db.getGuildSetting(ctx.guild.id,'coinname'))).embed)

    async def openAccount(self,user,guildid):
        if user.id not in self.db.getDiscordUserList(guildid):
            self.db.addUser(user.id,guildid,self.defaultUserSettings)
            self.logger.info(f"Account opened: guild={self.bot.get_guild(guildid)} ({guildid}) user={user.name}#{user.discriminator}")

    def failrate(self,guildid,job):
        if job=="heist": return 20
        return self.db.getGuildSetting(guildid,f"failrates_{job}")

    def payout(self,guildid,job):
        return random.randint(self.db.getGuildSetting(guildid,f"payouts_{job}_min"),self.db.getGuildSetting(guildid,f"payouts_{job}_max"))

    def fine(self,guildid,job):
        if job=="heist": return random.randint(500,2500)
        return random.randint(self.db.getGuildSetting(guildid,f"fines_{job}_min"),self.db.getGuildSetting(guildid,f"fines_{job}_max"))

    def logcommand(self,ctx): self.logger.info(f"COMMAND: guild={ctx.guild.name} ({ctx.guild.id}) user={ctx.author.name}#{ctx.author.discriminator} \"{ctx.message.content}\"")

    # ADMIN COMMANDS

    @commands.command()
    async def registerserver(self,ctx):
        """Enable the Economy system for the current server, which includes the Game and Shop systems
        Arguments: None
        Permission required: administrator
        Aliases: None"""
        self.logcommand(ctx)

        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id == 879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="administrator").embed)
                return
            guild=ctx.guild
            if guild.id not in self.db.getGuildList():
                self.db.createGuild(guild.id,self.defaultGuildSettings)
                await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.SERVER_REGISTERED,fields=[["⠀",strings.ADMIN_ECONOMY_SETTINGS]]).embed)
                return
        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.error,message=strings.SERVER_ALREADY_REGISTERED).embed)

    @commands.command()
    async def resetserversettings(self,ctx):
        self.logcommand(ctx)
        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id == 879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="administrator").embed)
                return
            guild=ctx.guild
            guildid=guild.id
            s=self.defaultGuildSettings

            await ctx.send(strings.NO)
            return

            self.db.execute(
                f'REPLACE INTO Guild VALUES ({guildid},{s["commandsUntilCooldown"]["work"]},{s["commandsUntilCooldown"]["crime"]},{s["commandsUntilCooldown"]["rob"]},{s["commandsUntilCooldown"]["slut"]},{s["commandsUntilCooldown"]["beg"]},{s["commandsUntilCooldown"]["withdraw"]},{s["commandsUntilCooldown"]["deposit"]},{s["cooldowns"]["work"]},{s["cooldowns"]["crime"]},{s["cooldowns"]["rob"]},{s["cooldowns"]["slut"]},{s["cooldowns"]["beg"]},{s["cooldowns"]["withdraw"]},{s["cooldowns"]["deposit"]},{s["payouts"]["crime"]["max"]},{s["payouts"]["crime"]["min"]},{s["payouts"]["work"]["max"]},{s["payouts"]["work"]["min"]},{s["payouts"]["slut"]["max"]},{s["payouts"]["slut"]["min"]},{s["failrates"]["crime"]},{s["failrates"]["rob"]},{s["failrates"]["slut"]},{s["fines"]["crime"]["max"]},{s["fines"]["crime"]["min"]},{s["fines"]["work"]["max"]},{s["fines"]["work"]["min"]},{s["fines"]["slut"]["max"]},{s["fines"]["slut"]["min"]},{s["betting"]["max"]},{s["betting"]["min"]},{s["shop"]["chicken"]["price"]},{s["shop"]["chicken"]["max"]},{s["shop"]["nft"]["price"]},{s["shop"]["nft"]["max"]},{s["wallet_max"]},{s["interest"]},{s["reply"]},{s["commandsUntilCooldownResetTime"]},"{s["coinname"]}",{s["defaultLeaderboardEntries"]})'
            )

            strings.DONE
            return

    @commands.command()
    async def setuserbalance(self,ctx,user:discord.Member=None,store=None,amount=None):
        self.logcommand(ctx)
        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id == 879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return

            coinname=self.db.getGuildSetting(ctx.guild.id, "coinname")

            if user==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_USER).embed)
                return
            await self.openAccount(user, ctx.guild.id)

            if store not in ["wallet","bank"]:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_MONEY_STORE).embed)
                return

            if amount==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_AMOUNT).embed)
                return

            amount=int(amount)

            if amount<=0:
                await ctx.send(embed=InvalidIntEmbed(ctx=ctx).embed)
                return

            self.db.setUserSetting(user.id,ctx.guild.id,store,amount)

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_GAVE%(user.display_name,humanize.humanizeNumber(amount),coinname)).embed)

    @commands.command()
    async def setusercooldown(self,ctx,user:discord.Member=None,command=None):
        self.logcommand(ctx)
        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return

            coinname=self.db.getGuildSetting(ctx.guild.id,"coinname")

            if user==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_USER).embed)
                return
            await self.openAccount(user,ctx.guild.id)

            if command==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_COMMAND).embed)
                return

            self.db.setUserSetting(user.id,ctx.guild.id,f"commandsUntilCooldownRemaining_{command}",self.db.getGuildSetting(ctx.guild.id,f"commandsUntilCooldown_{command}"))

            self.db.setUserSetting(user.id,ctx.guild.id,f"cooldowns_{command}",self.db.getGuildSetting(ctx.guild.id, f"cooldowns_{command}"))

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_RESET_COOLDOWN%(user.display_name,command)).embed)

    @commands.command()
    async def setserversetting(self,ctx,key,value):
        self.logcommand(ctx)
        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id==879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx,permission="administrator").embed)
                return

            self.db.setGuildSetting(ctx.guild.id,key,value)
            await ctx.send(strings.DONE)
            return

    @commands.command()
    async def setusersetting(self,ctx,user:discord.Member,key,value):
        self.logcommand(ctx)
        async with ctx.typing():
            if (not ctx.message.author.guild_permissions.administrator) and (not ctx.message.author.id == 879801241859915837):
                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="administrator").embed)
                return

            await self.openAccount(user, ctx.guild.id)

            self.db.setUserSetting(user.id, ctx.guild.id, key, value)
            await ctx.send(strings.DONE)
            return

    # GENERAL COMMANDS

    @commands.command(aliases=["bal","b"])
    async def balance(self,ctx,user:discord.Member=None):
        """Displays the balance of the sender or any other user
        Arguments: user, optional, user ping of the user you want to see the balance of
        Permission required: None
        Aliases: bal, b"""
        self.logcommand(ctx)

        async with ctx.typing():
            if user is None: user=ctx.author
            await self.openAccount(user,ctx.guild.id)

            coinname=self.db.getGuildSetting(ctx.guild.id,"coinname")
            balances=self.db.getUserBalances(user.id,ctx.guild.id)

        await ctx.send(embed=Embed(ctx=ctx,fields=[[strings.BAL_WALLET,f"{humanize.humanizeNumber(balances[0])} {coinname}"],[strings.BAL_BANK,f"{humanize.humanizeNumber(balances[1])} {coinname}"]],inline=True).embed)

    @commands.command(aliases=["lb"])
    async def leaderboard(self,ctx,amount=None):
        """Displays the total balances of the richest server users
        Arguments: amount, optional, defaults to 10 (can be changed in settings), defines the amount of users listed
        Permission required: None
        Aliases: lb"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname=self.db.getGuildSetting(ctx.guild.id, "coinname")

            if amount==None: amount=self.db.getGuildSetting(ctx.guild.id,"defaultLeaderboardEntries")
            elif not amount.isdigit():
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.AMOUNT_WHOLE_NUMBER).embed)
                return

            lb={};total=[];amount=int(amount)

            for user in self.db.getUserIds(ctx.guild.id)[:amount]:
                balances=self.db.getUserBalances(user,ctx.guild.id)
                lb[str(balances[0]+balances[1])]=user
                total.append(balances[0]+balances[1])

            total=sorted(total,reverse=True);index=1;f=[];changeAmt=True

            for amt in total:
                f.append([f"{index}. {self.bot.get_user(lb[str(amt)]).display_name}",f"{humanize.humanizeNumber(amt)} {coinname}"])
                if index==amount:
                    changeAmt=False
                    break
                else: index+=1

            if changeAmt: amount=len(total)

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.passive,message=strings.TOP_RICHEST_PEOPLE%(amount),fields=f).embed)

    @commands.command(aliases=["wd"])
    async def withdraw(self,ctx,amount=None):
        """Move money from your bank to your wallet
        Arguments: amount, required, a positive non-zero number less than or equal to your bank balance or "all"
        Permission required: None
        Aliases: wd"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            await self.openAccount(user, ctx.guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown=self.db.getGuildSetting(ctx.guild.id,"commandsUntilCooldown_withdraw")
            commandsUntilCooldownRemaining=self.db.getUserSetting(user.id, ctx.guild.id,"commandsUntilCooldownRemaining_withdraw")
            firstCommandExecuted=self.db.getUserSetting(user.id,ctx.guild.id,"firstCommandExecuted_withdraw")
            cooldownLength=self.db.getGuildSetting(ctx.guild.id,"cooldowns_withdraw")

            if commandsUntilCooldownRemaining==0:  # if the cooldown is active (at 0)
                cooldowns=self.db.getUserSetting(user.id,ctx.guild.id,"cooldowns_withdraw")
                cooldowndiff=cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff>=cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_withdraw",commandsUntilCooldown)
                    commandsUntilCooldownRemaining=commandsUntilCooldown
                    self.db.setUserSetting(user.id,ctx.guild.id,"firstCommandExecuted_withdraw",'""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"withdraw any {coinname}",remainingTime=cooldownLength-cooldowndiff).embed)
                    return

            if firstCommandExecuted!="":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted))>self.db.getGuildSetting(ctx.guild.id,"commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_withdraw",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining==commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id,ctx.guild.id,"firstCommandExecuted_withdraw",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining==1:
                self.db.setUserSetting(user.id,ctx.guild.id,"cooldowns_withdraw",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if amount==None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.SPECIFY_AMOUNT).embed)
                return

            bal=self.db.getUserBalances(user.id, ctx.guild.id)[1]
            if bal<0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.WITHDRAW_DEBT).embed)
                return
            elif bal==0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.WITHDRAW_ZERO%(coinname)).embed)
                return
            if amount.lower()=="all": amount=bal

            elif not amount.isdigit():
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.AMOUNT_WHOLE_NUMBER).embed)
                return

            amount=int(amount)

            if amount>bal:
                await ctx.send(embed=BankAmountInsufficientEmbed(ctx=ctx, coinname=coinname).embed)
                return
            if amount<=0:
                await ctx.send(embed=InvalidIntEmbed(ctx=ctx).embed)
                return

            self.db.updateUserBalance(user.id,ctx.guild.id,amount,"wallet")
            self.db.updateUserBalance(user.id,ctx.guild.id,-1*amount,"bank")

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_WITHDREW%(humanize.humanizeNumber(amount),coinname)).embed)
        await self.newWalletBalance(ctx)
        await self.newBankBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining=self.db.getUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_withdraw")
        if commandsUntilCooldownRemaining>0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_withdraw",wrapQuotes(commandsUntilCooldownRemaining-1))

    @commands.command(aliases=["dp"])
    async def deposit(self,ctx,amount=None):
        """Move money from your wallet to your bank
        Arguments: amount, required, a positive non-zero number less than or equal to your wallet balance or "all"
        Permission required: None
        Aliases: dp"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            await self.openAccount(user, ctx.guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(ctx.guild.id, "commandsUntilCooldown_deposit")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, ctx.guild.id,"commandsUntilCooldownRemaining_deposit")
            firstCommandExecuted = self.db.getUserSetting(user.id, ctx.guild.id, "firstCommandExecuted_deposit")
            cooldownLength = self.db.getGuildSetting(ctx.guild.id,"cooldowns_deposit")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, ctx.guild.id,"cooldowns_deposit")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, ctx.guild.id,"commandsUntilCooldownRemaining_deposit",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, ctx.guild.id,"firstCommandExecuted_deposit",'""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"deposit any {coinname}",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(ctx.guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_deposit",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, ctx.guild.id, "firstCommandExecuted_deposit",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(user.id, ctx.guild.id, "cooldowns_deposit",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if amount == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.SPECIFY_AMOUNT).embed)
                return

            bal = self.db.getUserBalances(user.id, ctx.guild.id)[0]
            if bal < 0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.DEPOSIT_DEBT).embed)
                return
            elif bal == 0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.DEPOSIT_ZERO%(coinname)).embed)
                return
            if amount.lower() == "all": amount = bal

            elif not amount.isdigit():
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.AMOUNT_WHOLE_NUMBER).embed)
                return

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=WalletAmountInsufficientEmbed(ctx=ctx, coinname=coinname).embed)
                return
            if amount <= 0:
                await ctx.send(embed=InvalidIntEmbed(ctx=ctx).embed)
                return

            self.db.updateUserBalance(user.id, ctx.guild.id, amount, "bank")
            self.db.updateUserBalance(user.id, ctx.guild.id, -1 * amount,"wallet")

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_DEPOSITED%(humanize.humanizeNumber(amount),coinname)).embed)
        await self.newWalletBalance(ctx)
        await self.newBankBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, ctx.guild.id, "commandsUntilCooldownRemaining_deposit")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_deposit",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["gift", "give"])
    async def send(self,ctx,sendto:discord.Member=None,amount=None):
        """Give money to someone else!
        It moves the money from your bank to their bank
        Arguments: sendto, required, user ping of the user you want to send the money to
        amount, required, a positive non-zero number less than or equal to your bank balance
        Permission required: None
        Aliases: gift, give"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            await self.openAccount(user, ctx.guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(ctx.guild.id, "commandsUntilCooldown_send")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, ctx.guild.id, "commandsUntilCooldownRemaining_send")
            firstCommandExecuted = self.db.getUserSetting(user.id, ctx.guild.id, "firstCommandExecuted_send")
            cooldownLength = self.db.getGuildSetting(ctx.guild.id,"cooldowns_send")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, ctx.guild.id,"cooldowns_send")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, ctx.guild.id,"commandsUntilCooldownRemaining_send",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, ctx.guild.id,"firstCommandExecuted_send", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"give anyone any more {coinname}",remainingTime=cooldownLength - cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(ctx.guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id,ctx.guild.id,"commandsUntilCooldownRemaining_send",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id,ctx.guild.id,"firstCommandExecuted_send",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(user.id,ctx.guild.id,"cooldowns_send",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if sendto == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.SPECIFY_USER).embed)
                return
            await self.openAccount(sendto, ctx.guild.id)

            if amount == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.SPECIFY_AMOUNT).embed)
                return

            bal = self.db.getUserBalances(user.id, ctx.guild.id)[1]

            if amount.lower() == "all":
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.CANT_SEND_ALL).embed)
                return

            elif not amount.isdigit():
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.AMOUNT_WHOLE_NUMBER).embed)
                return

            amount = int(amount)

            if amount > bal:
                await ctx.send(embed=BankAmountInsufficientEmbed(ctx=ctx, coinname=coinname).embed)
                return
            if amount <= 0:
                await ctx.send(embed=InvalidIntEmbed(ctx=ctx).embed)
                return

            self.db.updateUserBalance(user.id, ctx.guild.id, -1 * amount,"bank")
            self.db.updateUserBalance(sendto.id, ctx.guild.id, amount, "bank")

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_SENT%(humanize.humanizeNumber(amount),coinname,endto.display_name)).embed)
        self.newBankBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(
            user.id, ctx.guild.id, "commandsUntilCooldownRemaining_send")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, ctx.guild.id, "commandsUntilCooldownRemaining_send",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["cd"])
    async def cooldown(self,ctx,command=None,user2:discord.Member=None):
        self.logcommand(ctx)
        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            if command == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.SPECIFY_COMMAND).embed)
                return

            if user2 != None:user = user2

            cooldownLength = self.db.getGuildSetting(guild.id,f"cooldowns_{command}")
            cooldowns = self.db.getUserSetting(user.id, guild.id,f"cooldowns_{command}")
            cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(), cooldown.cooldownStrToObj(cooldowns))
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_work")

            if cooldowndiff >= cooldownLength:
                await ctx.send(embed=Embed(ctx=ctx,message=strings.NO_COOLDOWN%(user.name,command)).embed)
                return

            remtime = cooldownLength-cooldowndiff

        await ctx.send(embed=Embed(ctx=ctx,message=strings.COOLDOWN_OF%(command,user.name,humanize.humanizeSeconds(int(remtime)))).embed)

    # EARNING MONEY COMMANDS

    @commands.command(aliases=["w"])
    async def work(self,ctx):
        """Earn some money the good way!
        Arguments: None
        Permission required: None
        Aliases: w"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(guild.id, "commandsUntilCooldown_work")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_work")
            firstCommandExecuted = self.db.getUserSetting(user.id, guild.id, "firstCommandExecuted_work")
            cooldownLength = self.db.getGuildSetting(guild.id,"cooldowns_work")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, guild.id,"cooldowns_work")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_work",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, guild.id,"firstCommandExecuted_work", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"work",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_work",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, guild.id, "firstCommandExecuted_work",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(user.id, guild.id, "cooldowns_work",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            earning = self.payout(guild.id, "work")

            work = random.choice(replies.work()).replace("{amount}", f"{humanize.humanizeNumber(earning)} {coinname}")

            self.db.updateUserBalance(user.id, guild.id, earning, "wallet")

        await ctx.send(embed=Embed(ctx=ctx, type=EmbedType.success, message=work).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_work")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_work",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command()
    async def beg(self,ctx):
        """Earn some money the easy way!
        Arguments: None
        Permission required: None
        Aliases: None"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(guild.id, "commandsUntilCooldown_beg")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_beg")
            firstCommandExecuted = self.db.getUserSetting(user.id, guild.id, "firstCommandExecuted_beg")
            cooldownLength = self.db.getGuildSetting(guild.id, "cooldowns_beg")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, guild.id,"cooldowns_beg")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_beg",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, guild.id,"firstCommandExecuted_beg", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"beg",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_beg",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, guild.id, "firstCommandExecuted_beg",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1: self.db.setUserSetting(user.id, guild.id, "cooldowns_beg",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            p_earnings = []
            weights = []
            j = 10

            for i in range(20):
                for l in range(5):
                    weights.append(j)
                j -= 1

            earning = random.choices([x for x in range(100)],weights=tuple(weights),k=1)[0]

            self.db.updateUserBalance(user.id, guild.id, earning, "wallet")

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_BEGGED%(humanize.humanizeNumber(earning),coinname)).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_beg")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_beg",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["r"])
    async def rob(self,ctx,victim:discord.Member=None):
        """Earn some money the sneaky way!
        If you try to rob someone but they dont have any money, the cooldown is still activated
        Arguments: victim, required, the person you want to rob
        Permission required: None
        Aliases: r"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(guild.id, "commandsUntilCooldown_rob")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_rob")
            firstCommandExecuted = self.db.getUserSetting(user.id, guild.id, "firstCommandExecuted_rob")
            cooldownLength = self.db.getGuildSetting(guild.id, "cooldowns_rob")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, guild.id,"cooldowns_rob")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_rob",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, guild.id,"firstCommandExecuted_rob", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"rob anyone",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_rob",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, guild.id, "firstCommandExecuted_rob",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:self.db.setUserSetting(user.id, guild.id, "cooldowns_rob",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if victim == None:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.SPECIFY_USER).embed)
                return

            if victim.id == user.id:
                await ctx.send(embed=ErrorEmbed(ctx=ctx, message=strings.CANT_ROB_SELF).embed)
                return

            await self.openAccount(victim, ctx.guild.id)

            amount = int(self.db.getUserBalances(victim.id, ctx.guild.id)[0])

            if amount <= 0:
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.DOESNT_HAVE_MONEY%(victim.display_name)).embed)

                # the cooldown is decreased even if the victim has no money
                commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_rob")
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_rob",wrapQuotes(commandsUntilCooldownRemaining - 1))
                return

            earning = random.randint(amount // 2, amount)

            if False:#random.randint(1, 100) >= self.failrate(guild.id, "rob"):
                fine = self.fine(guild.id, "rob")
                self.db.updateUserBalance(user.id, guild.id, -1 * fine,"wallet")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.FAIL_ROB%(victim.display_name,humanize.humanizeNumber(fine),coinname)).embed)
                await self.newWalletBalance(ctx)
                commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_rob")
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_rob",wrapQuotes(commandsUntilCooldownRemaining - 1))
                return

            self.db.updateUserBalance(user.id, guild.id, earning, "wallet")
            self.db.updateUserBalance(victim.id, guild.id, earning * -1,"wallet")

        await ctx.send(embed=Embed(ctx=ctx,type=EmbedType.success,message=strings.YOU_ROBBED%(humanize.humanizeNumber(earning),coinname,victim.name)).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_rob")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_rob",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["c"])
    async def crime(self,ctx):
        """Earn some money the evil way!
        Beware, you might get caught...
        Arguments: None
        Permission required: None
        Aliases: c"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(guild.id, "commandsUntilCooldown_crime")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_crime")
            firstCommandExecuted = self.db.getUserSetting(user.id, guild.id, "firstCommandExecuted_crime")
            cooldownLength = self.db.getGuildSetting(guild.id,"cooldowns_crime")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, guild.id,"cooldowns_crime")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_crime",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, guild.id,"firstCommandExecuted_crime", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"commit a crime",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_crime",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, guild.id, "firstCommandExecuted_crime",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:self.db.setUserSetting(user.id, guild.id, "cooldowns_crime",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if random.randint(1, 100) >= self.failrate(guild.id, "crime"):
                fine = self.fine(guild.id, "crime")
                self.db.updateUserBalance(user.id, guild.id, -1 * fine,"wallet")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=strings.FAIL_CRIME%(humanize.humanizeNumber(fine),coinname)).embed)
                await self.newWalletBalance(ctx)
                commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_crime")
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_crime",wrapQuotes(commandsUntilCooldownRemaining - 1))
                return

            earning = self.payout(guild.id, "crime")
            crime = random.choice(replies.crime()).replace("{amount}", f"{humanize.humanizeNumber(earning)} {coinname}")

            self.db.updateUserBalance(user.id, guild.id, earning, "wallet")

        await ctx.send(embed=Embed(ctx=ctx, type=EmbedType.success, message=crime).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_crime")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_crime",wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["s"])
    async def slut(self,ctx):
        """Earn some money the schmexy way!
        Beware, you might get caught...
        Arguments: None
        Permission required: None
        Aliases: s"""
        self.logcommand(ctx)

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            commandsUntilCooldown = self.db.getGuildSetting(guild.id, "commandsUntilCooldown_slut")
            commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_slut")
            firstCommandExecuted = self.db.getUserSetting(user.id, guild.id, "firstCommandExecuted_slut")
            cooldownLength = self.db.getGuildSetting(guild.id,"cooldowns_slut")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(user.id, guild.id,"cooldowns_slut")
                cooldowndiff = cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_slut",commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(user.id, guild.id,"firstCommandExecuted_slut", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(ctx=ctx,message=f"be a slut",remainingTime=cooldownLength -cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(datetime.datetime.now(),cooldown.cooldownStrToObj(firstCommandExecuted)) > self.db.getGuildSetting(guild.id, "commandsUntilCooldownResetTime"):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_slut",wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(user.id, guild.id, "firstCommandExecuted_slut",wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:self.db.setUserSetting(user.id, guild.id, "cooldowns_slut",wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if random.randint(1, 100) >= self.failrate(guild.id, "slut"):
                fine = self.fine(guild.id, "slut")
                self.db.updateUserBalance(user.id, guild.id, -1 * fine,"wallet")
                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=random.choice(replies.slutFail()).replace("{amount}",f"{humanize.humanizeNumber(fine)} {coinname}")).embed)
                await self.newWalletBalance(ctx)
                commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_slut")
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(user.id, guild.id,"commandsUntilCooldownRemaining_slut",wrapQuotes(commandsUntilCooldownRemaining - 1))
                return

            earning = self.payout(guild.id, "slut")
            message = random.choice(replies.slutSuccess()).replace("{amount}", f"{humanize.humanizeNumber(earning)} {coinname}")

            self.db.updateUserBalance(user.id, guild.id, earning, "wallet")

        await ctx.send(embed=Embed(ctx=ctx, type=EmbedType.success, message=message).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_slut")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(user.id, guild.id, "commandsUntilCooldownRemaining_slut",wrapQuotes(commandsUntilCooldownRemaining - 1))

#    @commands.command(aliases=["h"])
#    async def heist(self,ctx):
#        async with ctx.typing():
#            if (not ctx.message.author.id == 879801241859915837):
#                await ctx.send(embed=PermissionErrorEmbed(ctx=ctx, permission="tom").embed)
#                return
#
#            """
#
#            There is a 80% chance of this command failing, and the user being put in prison. If put in prison, the user cannot use any economy commands for 2 days. There is 60% chance of getting fined 500£ to 2500£, with random generation of how much
#
#            If you succeed, then 5 bank accounts are randomly selected from the top 10
#
#
#
#            """
#
#            if random.randint(1, 100) >= self.failrate(guild.id, "heist") or True:
#                fine = self.fine(guild.id, "heist") if random.randint(1,10) > 4 else 0
#                #self.db.updateUserBalance(user.id, guild.id, -1 * fine,"bank")
#                await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"YOUR HEIST FAILED!",fields=[["You and your team were put in prison for 2 days - you can't use any economy commands until you are set free"],["You can see when you are let out by using the \"prison\" command"],[f"You were fined {fine} {self.coinname}" if fine > 0 else "You were lucky in court and were not fined"]]).embed)
#
#                await self.newBankBalance(ctx)
#            else:
#                await ctx.send(embed=Embed(ctx=ctx,type=ErrorEmbed.success,message="The heist was successful. (this aint implemnented yet :))"))

#    @commands.command(aliases=["p"])
#    async def prison(self,ctx,user_:discord.Member=None):
#        async with ctx.typing():
#            user=ctx.author
#            if user_!=None: user=user_
#            # if user in prison
#            if False: await ctx.send(embed=Embed(ctx=ctx,message=f"{user if user!=ctx.author else 'You'} are currently in prison",fields=[["You will be let out on [date]"]]))
#            else: await ctx.send(embed=Embed(ctx=ctx,message=f"{user if user!=ctx.author else 'You'} are not in prison"))

    # ERROR CATCHERS

    @balance.error
    @setuserbalance.error
    @setusercooldown.error
    @setusersetting.error
    @send.error
    @rob.error
    async def userInputError(self,ctx,error):
        if isinstance(error, discord.ext.commands.errors.MemberNotFound): await ctx.send(embed=ErrorEmbed(ctx=ctx,message=f"The user `{error.argument}` was not found").embed)
        else: self.logger.error(error)


def setup(bot,database,logger): bot.add_cog(Economy(bot,database,logger))
