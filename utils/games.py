import random, enum, discord
from utils.emoji import getCard, getEmoji
from utils.embed import Embed, EmbedType
from .assets import strings,config

class BlackjackGame:
    def __init__(self,ctx):
        class Suits(enum.Enum):
            spades=0
            clubs=1
            hearts=2
            diamonds=3
        class WinConditions(enum.Enum):
            playerBlackJack=0
            playerBust=1
            playerHigher=2
            dealerBlackJack=3
            dealerBust=4
            dealerHigher=5
            draw=6
        class Card:
            def __init__(self,suit:Suits=Suits.spades,value="A",valueint=11,emojiTag="AS"):
                self.suit=suit
                self.value=value
                self.valueint=valueint
                self.emojiTag=emojiTag

        self.Suits=Suits
        self.WinConditions=WinConditions
        self.Card=Card

        self.ctx=ctx
        self.initialiseDeck()

    def dealCard(self):
        card=random.choice(self.deck)
        self.deck.remove(card)
        return card

    def initialiseDeck(self):
        suits=[self.Suits.spades,self.Suits.clubs,self.Suits.hearts,self.Suits.diamonds]
        suitTags={self.Suits.spades:"S",self.Suits.clubs:"C",self.Suits.hearts:"H",self.Suits.diamonds:"D"}
        cards=["A","2","3","4","5","6","8","9","10","J","Q","K"]
        cardValues = {"A": 11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}
        self.deck=[]
        for suit in suits:
            for card in cards:
                self.deck.append(self.Card(suit,card,cardValues[card],f"{card}{suitTags[suit]}"))

    def checkAcePlayer(self):
        for card in self.pc:
            if card.valueint == 11:
                card.valueint = 1
                self.ps -= 10
                return

    def checkAceDealer(self):
        for card in self.dc:
            if card.valueint == 11:
                card.valueint = 1
                self.ds -= 10
                return

    async def hitOrStand(self):
        response = await self.ctx.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        while response.content.lower() not in ["hit","stick"]:
            await self.ctx.send(strings.INVALID_INPUT)
            response = await self.ctx.bot.wait_for('message', check=lambda message: message.author == self.ctx.author)
        return response.content.lower() == "hit"

    def dealPlayer(self):
        card=self.dealCard()
        self.pc.append(card)
        self.ps+=card.valueint

    def dealDealer(self):
        card=self.dealCard()
        self.dc.append(card)
        self.ds+=card.valueint

    async def game(self):
        # SETUP PLAYER DECK
        breaker=True
        while breaker:
            self.pc=[]
            self.ps=0

            self.dealPlayer()
            self.dealPlayer()

            if self.ps < 21: breaker=False

        # SETUP DEALER DECK
        breaker=True
        while breaker:
            self.dc=[]
            self.ds=0

            self.dealDealer()
            self.dealDealer()

            if self.ds < 21: breaker=False

        # PLAYER'S GO
        breaker=True
        while breaker:
            await self.ctx.send(embed=self.outputCurrentScores(self.ctx.author,self.pc,self.dc,self.ps,len(self.deck)))
            if await self.hitOrStand():
                self.dealPlayer()
                if self.ps > 21: self.checkAcePlayer() # convert ace as 11 to ace as 1
            else: breaker=False
            if self.ps > 20: breaker=False

        # CHECK PLAYER BLACKJACK OR BUST
        if self.ps==21: return self.endGame(self.WinConditions.playerBlackJack)
        if self.ps > 21: return self.endGame(self.WinConditions.playerBust)

        # DEALER'S GO
        while self.ds < 17:
            self.dealDealer()
            if self.ds > 21: self.checkAceDealer()

        # CHECK DEALER BLACKJACK OR BUST
        if self.ds==21: return self.endGame(self.WinConditions.dealerBlackJack)
        if self.ds > 21: return self.endGame(self.WinConditions.dealerBust)

        if self.ps==self.ds:
            return self.endGame(self.WinConditions.draw)

        if self.ps>self.ds:
            return self.endGame(self.WinConditions.playerHigher)

        return self.endGame(self.WinConditions.dealerHigher)

    def endGame(self,wincondition):
        return self.outputOutcome(self.ctx.author,self.pc,self.dc,wincondition)

    def outputOutcome(self,user,pc,dc,wincondition):
        result=""
        result1=""
        if wincondition == self.WinConditions.playerBlackJack: result=strings.RESULT_BLACKJACK
        if wincondition == self.WinConditions.playerBust: result=strings.RESULT_BLACKJACK
        if wincondition == self.WinConditions.playerHigher: result=strings.RESULT_BUST
        if wincondition == self.WinConditions.dealerBlackJack: result=strings.RESULT_DBLACKJACK
        if wincondition == self.WinConditions.dealerBust: result=strings.RESULT_DBUST
        if wincondition == self.WinConditions.dealerHigher: result=strings.RESULT_LOSE
        if wincondition == self.WinConditions.draw: result=strings.RESULT_DRAW

        color=0xa3a3a3
        result1="draw"
        type=EmbedType.gray

        if wincondition in [self.WinConditions.playerBlackJack,self.WinConditions.playerHigher,self.WinConditions.dealerBust]:
            color=0x66bb6a
            result1="win"
            type=EmbedType.success

        if wincondition in [self.WinConditions.dealerBlackJack,self.WinConditions.dealerHigher,self.WinConditions.playerBust]:
            color=0xEF5350
            type=EmbedType.error
            result1="loss"

        pcards=""
        for card in pc: pcards=pcards+getCard(card.emojiTag)
        pcards+="\n\n"+strings.VALUE % str(self.ps)

        dcards=""
        for card in dc: dcards=dcards+getCard(card.emojiTag)
        dcards+="\n\n"+strings.VALUE % str(self.ds)

        return Embed(
            ctx=self.ctx,
            type=type,
            message=strings.RESULT%result,
            fields=[[strings.YOUR_HAND,pcards],[strings.DEALERS_HAND,dcards]],
            inline=True,
        ).embed, result1

    def outputCurrentScores(self,user,pc,dc,ps,remaining):
        #embed=discord.Embed(title=" ", description=strings.HIT_OR_STICK, color=0x03a9f4)

        pcards=""
        for card in pc: pcards=pcards+getCard(card.emojiTag)
        pcards+="\n\n"+strings.VALUE % str(ps)

        dcards=getCard(dc[0].emojiTag)
        for i in range(len(dc)-1): dcards=dcards+getCard("CardBack")
        dcards+="\n\n"+strings.VALUE % "?"
        #embed.add_field(name=strings.YOUR_HAND,value=pcards,inline=True)
        #embed.add_field(name=strings.DEALERS_HAND,value=dcards,inline=True)
        #embed.set_author(name='{0.name}#{0.discriminator}'.format(user), icon_url=user.avatar_url)
        #embed.set_footer(text=strings.CARDS_REMAINING % remaining)
        #return embed

        return Embed(
            ctx=self.ctx,
            message=strings.HIT_OR_STICK,
            fields=[[strings.YOUR_HAND,pcards],[strings.DEALERS_HAND,dcards]],
            inline=True,
            footer=strings.CARDS_REMAINING % str(remaining)
        ).embed

async def startBlackjack(ctx):
    game=BlackjackGame(ctx)
    return await game.game()
