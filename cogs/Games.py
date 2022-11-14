import random, pickle, json, datetime
from discord.ext import commands
from utils import cooldown
from utils import formatting as humanize
from utils.items import newChicken
from utils.games import startBlackjack
from utils.other import csvToList, listToCsv, wrapQuotes
from utils.embed import Embed, EmbedType, CooldownEmbed, ErrorEmbed, WalletAmountInsufficientEmbed, BetTooLowEmbed, BetTooHighEmbed


class Games(commands.Cog):

    def __init__(self, bot, database):
        self.bot = bot
        self.db = database

        with open("data/defaultGuildSettings.json", "r") as f:
            self.defaultGuildSettings = json.load(f)
        with open("data/defaultUserSettings.json", "r") as f:
            self.defaultUserSettings = json.load(f)

    # UTILS

    async def newWalletBalance(self, ctx):
        await ctx.send(embed=Embed(
            ctx=ctx,
            message=
            f"Your new wallet balance is {humanize.humanizeNumber(self.db.getUserBalances(ctx.author.id,ctx.guild.id)[0])} {self.db.getGuildSetting(ctx.guild.id,'coinname')}"
        ).embed)

    async def newBankBalance(self, ctx):
        await ctx.send(embed=Embed(
            ctx=ctx,
            message=
            f"Your new bank balance is {humanize.humanizeNumber(self.db.getUserBalances(ctx.author.id,ctx.guild.id)[1])}"
        ).embed)

    async def openAccount(self, user, guildid):
        if user.id not in self.db.getDiscordUserList(guildid):
            self.db.addUser(user.id, guildid, self.defaultUserSettings)

    # GAMES

    @commands.command(aliases=["cf"])
    async def cockfight(self, ctx, bet=None):
        """Bet on your chicken and see who comes out on top!
        You play against a computer chicken.
        Arguments: bet, required, the amount of money you want to bet
        Permission required: None
        Aliases: cf"""

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            cooldownCommand = "cockfight"
            commandsUntilCooldown = self.db.getGuildSetting(
                guild.id, f"commandsUntilCooldown_{cooldownCommand}")
            commandsUntilCooldownRemaining = self.db.getUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}")
            firstCommandExecuted = self.db.getUserSetting(
                user.id, guild.id, f"firstCommandExecuted_{cooldownCommand}")
            cooldownLength = self.db.getGuildSetting(
                guild.id, f"cooldowns_{cooldownCommand}")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}")
                cooldowndiff = cooldown.cooldownDiff(
                    datetime.datetime.now(),
                    cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"firstCommandExecuted_{cooldownCommand}", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(embed=CooldownEmbed(
                        ctx=ctx,
                        message=f"send your chicken to fight",
                        remainingTime=cooldownLength - cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(
                        datetime.datetime.now(),
                        cooldown.cooldownStrToObj(firstCommandExecuted)
                ) > self.db.getGuildSetting(
                        guild.id, f"commandsUntilCooldownResetTime"
                ):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(
                    user.id, guild.id,
                    f"firstCommandExecuted_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if bet == None:
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message="You did not specify an amount to bet on").embed)
                return

            if not bet.isdigit():
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx, message="`Bet` needs to be a whole number").embed)
                return

            bet = int(bet)

            bal = self.db.getUserBalances(user.id, guild.id)[0]
            betmin = self.db.getGuildSetting(guild.id, "betting_min")
            betmax = self.db.getGuildSetting(guild.id, "betting_max")

            if bet > bal:
                await ctx.send(embed=WalletAmountInsufficientEmbed(
                    ctx=ctx).embed)
                return
            if bet < betmin:
                await ctx.send(embed=BetTooLowEmbed(ctx=ctx, min=betmin).embed)
                return
            if bet > betmax:
                await ctx.send(embed=BetTooHighEmbed(ctx=ctx, max=betmax).embed
                               )
                return

            #embed, error = await startCockfight(ctx,user,bet)
            userChickens = csvToList(
                self.db.getUserSetting(user.id, guild.id, "inventory_chicken"))

            if len(userChickens) < 1:
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message=
                    "You need to buy a chicken from the store first using `buy chicken`"
                ).embed)
                return

            chicken = pickle.loads(userChickens[0])
            opponent = newChicken()

            if chicken.strength >= opponent.strength:
                if opponent.strength > chicken.strength // 2:
                    chicken.strength -= opponent.strength // 12
                userChickens[0] = str(pickle.dumps(chicken))
                self.db.setUserSetting(user.id, guild.id, f"inventory_{item}",
                                       listToCsv(useritems))
                self.db.updateUserBalance(user.id, guild.id, bet, "wallet")
                await ctx.send(embed=Embed(
                    ctx=ctx,
                    type=EmbedType.success,
                    message=
                    f"Your lil chicken won the fight, and made you {bet} {coinname} richer! :rooster:",
                    footer=
                    f"Your Chicken's New Strength (used to determine winner): {chicken.strength}"
                ).embed)
                await self.newWalletBalance(ctx)
            else:
                # repickle dead chicken
                emoji = getEmoji("rip")
                self.db.updateUserBalance(user.id, guild.id, bet * -1,
                                          "wallet")
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx, message=f"Your chicken died {ripEmoji}").embed)
                await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(
            user.id, guild.id,
            f"commandsUntilCooldownRemaining_{cooldownCommand}")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}",
                wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command(aliases=["bj"])
    async def blackjack(self, ctx, bet=None):
        """Play blackjack against the computer, closest to 21 wins
        Arguments: bet, required, the amount of money you want to bet
        Permission required: None
        Aliases: bj"""

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            cooldownCommand = "blackjack"
            commandsUntilCooldown = self.db.getGuildSetting(
                guild.id, f"commandsUntilCooldown_{cooldownCommand}")
            commandsUntilCooldownRemaining = self.db.getUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}")
            firstCommandExecuted = self.db.getUserSetting(
                user.id, guild.id, f"firstCommandExecuted_{cooldownCommand}")
            cooldownLength = self.db.getGuildSetting(
                guild.id, f"cooldowns_{cooldownCommand}")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}")
                cooldowndiff = cooldown.cooldownDiff(
                    datetime.datetime.now(),
                    cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"firstCommandExecuted_{cooldownCommand}", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(
                        embed=CooldownEmbed(ctx=ctx,
                                            message=f"play blackjack",
                                            remainingTime=cooldownLength -
                                            cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(
                        datetime.datetime.now(),
                        cooldown.cooldownStrToObj(firstCommandExecuted)
                ) > self.db.getGuildSetting(
                        guild.id, f"commandsUntilCooldownResetTime"
                ):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(
                    user.id, guild.id,
                    f"firstCommandExecuted_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if bet == None:
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message="You did not specify an amount to bet on").embed)
                return

            if not bet.isdigit():
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx, message="`Bet` needs to be a whole number").embed)
                return

            bet = int(bet)

            bal = self.db.getUserBalances(user.id, guild.id)[0]
            betmin = self.db.getGuildSetting(guild.id, "betting_min")
            betmax = self.db.getGuildSetting(guild.id, "betting_max")

            if bet > bal:
                await ctx.send(embed=WalletAmountInsufficientEmbed(
                    ctx=ctx).embed)
                return
            if bet < betmin:
                await ctx.send(embed=BetTooLowEmbed(ctx=ctx, min=betmin).embed)
                return
            if bet > betmax:
                await ctx.send(embed=BetTooHighEmbed(ctx=ctx, max=betmax).embed
                               )
                return

            embed, result = await startBlackjack(ctx)

            await ctx.send(embed=embed)

            if result == "loss":
                self.db.updateUserBalance(user.id, guild.id, -1 * bet,
                                          "wallet")
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message=
                    f"You lost the game of blackjack and lost {humanize.humanizeNumber(bet)} {coinname}"
                ).embed)
                await self.newWalletBalance(ctx)
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        wrapQuotes(commandsUntilCooldownRemaining - 1))
                return
            if result == "draw":
                await ctx.send(embed=Embed(
                    ctx=ctx,
                    type=EmbedType.gray,
                    message=
                    f"You drew the game of blackjack and didn't get any {coinname}"
                ).embed)
                if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        wrapQuotes(commandsUntilCooldownRemaining - 1))
                return

        self.db.updateUserBalance(user.id, guild.id, bet, "wallet")

        await ctx.send(embed=Embed(
            ctx=ctx,
            type=EmbedType.success,
            message=
            f"You won the game of blackjack and recieved {humanize.humanizeNumber(bet)} {coinname} in return"
        ).embed)
        await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(
            user.id, guild.id,
            f"commandsUntilCooldownRemaining_{cooldownCommand}")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}",
                wrapQuotes(commandsUntilCooldownRemaining - 1))

    @commands.command()
    async def slots(self, ctx, bet=None):
        """Bet on the outcome of three spinny wheels
        Arguments: bet, required, the amount of money you want to bet
        Permission required: None
        Aliases: None"""

        async with ctx.typing():
            coinname = self.db.getGuildSetting(ctx.guild.id, "coinname")
            user = ctx.author
            guild = ctx.guild
            await self.openAccount(user, guild.id)

            # COOLDOWN HANDLING

            cooldownCommand = "slots"
            commandsUntilCooldown = self.db.getGuildSetting(
                guild.id, f"commandsUntilCooldown_{cooldownCommand}")
            commandsUntilCooldownRemaining = self.db.getUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}")
            firstCommandExecuted = self.db.getUserSetting(
                user.id, guild.id, f"firstCommandExecuted_{cooldownCommand}")
            cooldownLength = self.db.getGuildSetting(
                guild.id, f"cooldowns_{cooldownCommand}")

            if commandsUntilCooldownRemaining == 0:  # if the cooldown is active (at 0)
                cooldowns = self.db.getUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}")
                cooldowndiff = cooldown.cooldownDiff(
                    datetime.datetime.now(),
                    cooldown.cooldownStrToObj(cooldowns))

                if cooldowndiff >= cooldownLength:  # if the cooldown has completed, reset the cooldown stats and run the command
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        commandsUntilCooldown)
                    commandsUntilCooldownRemaining = commandsUntilCooldown
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"firstCommandExecuted_{cooldownCommand}", '""')

                else:  # if the cooldown is still active stop the command
                    await ctx.send(
                        embed=CooldownEmbed(ctx=ctx,
                                            message=f"use the slot machine",
                                            remainingTime=cooldownLength -
                                            cooldowndiff).embed)
                    return

            if firstCommandExecuted != "":
                if cooldown.cooldownDiff(
                        datetime.datetime.now(),
                        cooldown.cooldownStrToObj(firstCommandExecuted)
                ) > self.db.getGuildSetting(
                        guild.id, f"commandsUntilCooldownResetTime"
                ):  # if the time since the first command is greater than the command reset window time
                    self.db.setUserSetting(
                        user.id, guild.id,
                        f"commandsUntilCooldownRemaining_{cooldownCommand}",
                        wrapQuotes(commandsUntilCooldown))

            if commandsUntilCooldownRemaining == commandsUntilCooldown:  # if the first command has not yet been executed set the start time for the command reset window
                self.db.setUserSetting(
                    user.id, guild.id,
                    f"firstCommandExecuted_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            if commandsUntilCooldownRemaining == 1:
                self.db.setUserSetting(
                    user.id, guild.id, f"cooldowns_{cooldownCommand}",
                    wrapQuotes(cooldown.currentCooldownTime()))

            # COMMAND HANDLING

            if bet == None:
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message="You did not specify an amount to bet on").embed)
                return

            if not bet.isdigit():
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx, message="`Bet` needs to be a whole number").embed)
                return

            bet = int(bet)

            bal = self.db.getUserBalances(user.id, guild.id)[0]
            betmin = self.db.getGuildSetting(guild.id, "betting_min")
            betmax = self.db.getGuildSetting(guild.id, "betting_max")

            if bet > bal:
                await ctx.send(embed=WalletAmountInsufficientEmbed(
                    ctx=ctx).embed)
                return
            if bet < betmin:
                await ctx.send(embed=BetTooLowEmbed(ctx=ctx, min=betmin).embed)
                return
            if bet > betmax:
                await ctx.send(embed=BetTooHighEmbed(ctx=ctx, max=betmax).embed
                               )
                return

            #final = []
            #for i in range(3):
            #    a = random.choice([':star:',':star:',':apple:',':apple:',':banana:',':banana:',':tangerine:',':tangerine:',':skull:'])
            #    final.append(a)

            final = random.choices(
                [':star:', ':apple:', ':banana:', ':tangerine:', ':skull:'],
                weights=[2, 2, 2, 2, 1],
                k=3)

            if user.id == 879801241859915837:
                final = random.choices([
                    ':star:', ':apple:', ':banana:', ':tangerine:', ':skull:'
                ],
                                       weights=[4, 2, 2, 2, 1],
                                       k=3)

            f = [[final[0], "Slot1"], [final[1], "Slot2"], [final[2], "Slot3"]]

            if final[0] == final[1] or final[1] == final[2] or final[
                    0] == final[2]:  # if two or more are the same
                if final.count(":skull:") > 1:  # if more than one is a skull
                    if final[0] == final[1] == final[2]:  # if all are skulls
                        self.db.updateUserBalance(user.id, ctx.guild.id,
                                                  bet * -4, "wallet")
                        await ctx.send(embed=ErrorEmbed(
                            ctx=ctx,
                            message=
                            f"You rolled three skulls and lost {humanize.humanizeNumber(bet*4)} {coinname}",
                            fields=f,
                            inline=True).embed)
                    else:  # if two are skulls
                        self.db.updateUserBalance(user.id, ctx.guild.id,
                                                  bet * -2, "wallet")
                        await ctx.send(embed=ErrorEmbed(
                            ctx=ctx,
                            message=
                            f"You rolled two skulls and lost {humanize.humanizeNumber(bet*2)} {coinname}",
                            fields=f,
                            inline=True).embed)
                elif ":star:" in final and final[0] == final[1] == final[
                        2]:  # if all are stars
                    self.db.updateUserBalance(user.id, ctx.guild.id, bet * 4,
                                              "wallet")
                    await ctx.send(embed=ErrorEmbed(
                        ctx=ctx,
                        message=
                        f"You rolled three stars and gained {humanize.humanizeNumber(bet*4)} {coinname}",
                        fields=f,
                        inline=True).embed)
                elif final[0] == final[1] == final[2]:  # if all are the same
                    self.db.updateUserBalance(user.id, ctx.guild.id, bet * 3,
                                              "wallet")
                    await ctx.send(embed=ErrorEmbed(
                        ctx=ctx,
                        message=
                        f"You rolled three identical items and gained {humanize.humanizeNumber(bet*3)} {coinname}",
                        fields=f,
                        inline=True).embed)
                else:  # if two are the same
                    self.db.updateUserBalance(user.id, ctx.guild.id, bet * 2,
                                              "wallet")
                    await ctx.send(embed=ErrorEmbed(
                        ctx=ctx,
                        message=
                        f"You rolled two identical items and gained {humanize.humanizeNumber(bet*2)} {coinname}",
                        fields=f,
                        inline=True).embed)
            else:  # if none are the same
                self.db.updateUserBalance(user.id, ctx.guild.id, bet * -1,
                                          "wallet")
                await ctx.send(embed=ErrorEmbed(
                    ctx=ctx,
                    message=
                    f"You didn't role anything good and lost {humanize.humanizeNumber(bet)} {coinname}",
                    fields=f,
                    inline=True).embed)

            await self.newWalletBalance(ctx)

        # make sure the amount of allowed commands remaining is decreased
        commandsUntilCooldownRemaining = self.db.getUserSetting(
            user.id, guild.id,
            f"commandsUntilCooldownRemaining_{cooldownCommand}")
        if commandsUntilCooldownRemaining > 0:  # decrease cooldown value by 1
            self.db.setUserSetting(
                user.id, guild.id,
                f"commandsUntilCooldownRemaining_{cooldownCommand}",
                wrapQuotes(commandsUntilCooldownRemaining - 1))


def setup(bot, database):
    bot.add_cog(Games(bot, database))
