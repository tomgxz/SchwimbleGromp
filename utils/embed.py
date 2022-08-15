import enum, discord
from .formatting import humanizeSeconds

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
        if footer == None: self.embed.set_footer(text=f"Original command: {ctx.message.content}")
        else: self.embed.set_footer(text=f"{footer}\nOriginal command: {ctx.message.content}")

    def getColor(self,type:EmbedType):
        if type == EmbedType.success:
            return 0x66bb6a
        if type == EmbedType.error:
            return 0xEF5350
        if type == EmbedType.announcement:
            return 0x17d1af
        if type == EmbedType.gray:
            return 0xa3a3a3
        return 0x03a9f4

class ErrorEmbed(Embed):
    def __init__(self,ctx=None,message="MESSAGE",fields=[[]],inline=False,footer=None):
        super().__init__(ctx=ctx,type=EmbedType.error,message=message,fields=fields,inline=inline,footer=footer)

class PermissionErrorEmbed(ErrorEmbed):
    def __init__(self,ctx=None,permission="administrator"):
        super().__init__(ctx=ctx,message=f"You need the {permission} permission to run this command")

class BankAmountInsufficientEmbed(ErrorEmbed):
    def __init__(self,ctx=None,coinname=None):
        super().__init__(ctx=ctx,message=f"You do not have enough {coinname if coinname is not None else 'money'} in your bank")

class WalletAmountInsufficientEmbed(ErrorEmbed):
    def __init__(self,ctx=None,coinname=None):
        super().__init__(ctx=ctx,message=f"You do not have enough {coinname if coinname is not None else 'money'} in your wallet")

class InvalidIntEmbed(ErrorEmbed):
    def __init__(self,ctx=None):
        super().__init__(ctx=ctx,message="Amount must be positive and not zero")

class CooldownEmbed(ErrorEmbed):
    def __init__(self,ctx=None,message="use this command",remainingTime=0,job=None):
        message=f"You cannot {message} for another {humanizeSeconds(int(remainingTime))}"
        super().__init__(ctx=ctx,message=message)

class BetTooLowEmbed(ErrorEmbed):
    def __init__(self,ctx=None,min=0,coinname=""):
        super().__init__(ctx=ctx,message=f"You must bet at least {min} {coinname}")

class BetTooHighEmbed(ErrorEmbed):
    def __init__(self,ctx=None,max=0,coinname=""):
        super().__init__(ctx=ctx,message=f"You cannot bet more than {max} {coinname}")
