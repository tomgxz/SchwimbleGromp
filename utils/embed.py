import enum, discord
from .formatting import humanizeSeconds
from .assets import strings, config

class EmbedType(enum.Enum):
    success=0
    error=1
    passive=2
    other=3
    announcement=4
    gray=5

class Embed():
    def __init__(self,ctx=None,type:EmbedType=EmbedType.passive,message=" ",fields=[[]],inline=False,footer=None):
        self.embed=discord.Embed(title=" ",description=message,color=self.getColor(type))
        if fields != [[]]:
            for i in range(len(fields)):
                self.embed.add_field(name=fields[i][0],value=fields[i][1],inline=inline)
        self.embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",icon_url=ctx.author.avatar_url)
        if footer == None: self.embed.set_footer(text=strings.ORIGINAL_COMMAND%ctx.message.content)
        else: self.embed.set_footer(text=footer+"\n"+strings.ORIGINAL_COMMAND%ctx.message.content)

    def getColor(self,type:EmbedType):
        if type == EmbedType.success: return config.COLOR_SUCCESS
        if type == EmbedType.error: return config.COLOR_ERROR
        if type == EmbedType.announcement: return config.COLOR_ANNOUNCEMENT
        if type == EmbedType.gray: return config.COLOR_GRAY
        return config.COLOR_PASSIVE

class ErrorEmbed(Embed):
    def __init__(self,ctx=None,message="MESSAGE",fields=[[]],inline=False,footer=None):
        super().__init__(ctx=ctx,type=EmbedType.error,message=message,fields=fields,inline=inline,footer=footer)

class PermissionErrorEmbed(ErrorEmbed):
    def __init__(self,ctx=None,permission="administrator"):
        super().__init__(ctx=ctx,message=strings.PERMISSION_ERROR % permission)

class BankAmountInsufficientEmbed(ErrorEmbed):
    def __init__(self,ctx=None,coinname=None):
        super().__init__(ctx=ctx,message=strings.BANK_INSUFFICIENT % (coinname if coinname is not None else 'money'))

class WalletAmountInsufficientEmbed(ErrorEmbed):
    def __init__(self,ctx=None,coinname=None):
        super().__init__(ctx=ctx,message=strings.WALLET_INSUFFICIENT % (coinname if coinname is not None else 'money'))

class InvalidIntEmbed(ErrorEmbed):
    def __init__(self,ctx=None):
        super().__init__(ctx=ctx,message=strings.INVALID_INT % "amount")

class CooldownEmbed(ErrorEmbed):
    def __init__(self,ctx=None,message="use this command",remainingTime=0,job=None):
        message=strings.COOLDOWN_ERROR % (message, humanizeSeconds(int(remainingTime)))
        super().__init__(ctx=ctx,message=message)

class BetTooLowEmbed(ErrorEmbed):
    def __init__(self,ctx=None,min=0,coinname=""):
        super().__init__(ctx=ctx,message=strings.BET_TOO_LOW % (min,coinname))

class BetTooHighEmbed(ErrorEmbed):
    def __init__(self,ctx=None,max=0,coinname=""):
        super().__init__(ctx=ctx,message=strings.BET_TOO_HIGH % (min,coinname))
