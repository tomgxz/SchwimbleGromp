import sqlite3
from utils.other import wrapQuotes


class Database():

    def __init__(self):
        self.connection = sqlite3.connect("data/economydata.db")
        self.cursor = self.connection.cursor()
        self.execute("PRAGMA foreign_keys = ON")
        self.execute("""
CREATE TABLE IF NOT EXISTS Guild (
guildid INTEGER PRIMARY KEY,
commandsUntilCooldown_work INTEGER,
commandsUntilCooldown_crime INTEGER,
commandsUntilCooldown_rob INTEGER,
commandsUntilCooldown_slut INTEGER,
commandsUntilCooldown_beg INTEGER,
commandsUntilCooldown_withdraw INTEGER,
commandsUntilCooldown_deposit INTEGER,
commandsUntilCooldown_send INTEGER,
commandsUntilCooldown_cockfight INTEGER,
commandsUntilCooldown_blackjack INTEGER,
commandsUntilCooldown_slots INTEGER,
commandsUntilCooldown_buy INTEGER,
cooldowns_work INTEGER,
cooldowns_crime INTEGER,
cooldowns_rob INTEGER,
cooldowns_slut INTEGER,
cooldowns_beg INTEGER,
cooldowns_withdraw INTEGER,
cooldowns_deposit INTEGER,
cooldowns_send INTEGER,
cooldowns_cockfight INTEGER,
cooldowns_blackjack INTEGER,
cooldowns_slots INTEGER,
cooldowns_buy INTEGER,
payouts_crime_max INTEGER,
payouts_crime_min INTEGER,
payouts_work_max INTEGER,
payouts_work_min INTEGER,
payouts_slut_max INTEGER,
payouts_slut_min INTEGER,
failrates_crime INTEGER,
failrates_rob INTEGER,
failrates_slut INTEGER,
fines_crime_max INTEGER,
fines_crime_min INTEGER,
fines_work_max INTEGER,
fines_work_min INTEGER,
fines_slut_max INTEGER,
fines_slut_min INTEGER,
betting_max INTEGER,
betting_min INTEGER,
shop_availableItems TEXT,
shop_chicken_price INTEGER,
shop_chicken_max INTEGER,
shop_nft_price INTEGER,
shop_nft_max INTEGER,
walletmax INTEGER,
interest INTEGER,
reply INTEGER,
commandsUntilCooldownResetTime INTEGER,
coinname TEXT,
defaultLeaderboardEntries INTEGER)
""")
        self.execute("""
CREATE TABLE IF NOT EXISTS User (
economyuserid INTEGER PRIMARY KEY AUTOINCREMENT,
discorduserid INTEGER,
guildid INTEGER,
commandsUntilCooldownRemaining_work INTEGER,
commandsUntilCooldownRemaining_crime INTEGER,
commandsUntilCooldownRemaining_rob INTEGER,
commandsUntilCooldownRemaining_slut INTEGER,
commandsUntilCooldownRemaining_beg INTEGER,
commandsUntilCooldownRemaining_withdraw INTEGER,
commandsUntilCooldownRemaining_deposit INTEGER,
commandsUntilCooldownRemaining_send INTEGER,
commandsUntilCooldownRemaining_cockfight INTEGER,
commandsUntilCooldownRemaining_blackjack INTEGER,
commandsUntilCooldownRemaining_slots INTEGER,
commandsUntilCooldownRemaining_buy INTEGER,
firstCommandExecuted_work TEXT,
firstCommandExecuted_crime TEXT,
firstCommandExecuted_rob TEXT,
firstCommandExecuted_slut TEXT,
firstCommandExecuted_beg TEXT,
firstCommandExecuted_withdraw TEXT,
firstCommandExecuted_deposit TEXT,
firstCommandExecuted_send TEXT,
firstCommandExecuted_cockfight TEXT,
firstCommandExecuted_blackjack TEXT,
firstCommandExecuted_slots TEXT,
firstCommandExecuted_buy TEXT,
cooldowns_work TEXT,
cooldowns_crime TEXT,
cooldowns_rob TEXT,
cooldowns_slut TEXT,
cooldowns_beg TEXT,
cooldowns_withdraw TEXT,
cooldowns_deposit TEXT,
cooldowns_send TEXT,
cooldowns_cockfight TEXT,
cooldowns_blackjack TEXT,
cooldowns_slots TEXT,
cooldowns_buy TEXT,
inventory_chicken TEXT,
inventory_nft TEXT,
wallet INT,
bank INT,
winnings INT,
losses INT,
FOREIGN KEY(guildid) REFERENCES Guild(guildid) )""")

    def __del__(self):
        self.connection.close()

    def execute(self, command):
        self.cursor.execute(command)
        self.connection.commit()

    def getGuildList(self):
        self.cursor.execute("SELECT * FROM Guild")
        return [x[0] for x in self.cursor.fetchall()]

    def createGuild(self, guildid, s):
        self.execute(f'''INSERT INTO Guild VALUES (
{guildid},
{s["commandsUntilCooldown"]["work"]},
{s["commandsUntilCooldown"]["crime"]},
{s["commandsUntilCooldown"]["rob"]},
{s["commandsUntilCooldown"]["slut"]},
{s["commandsUntilCooldown"]["beg"]},
{s["commandsUntilCooldown"]["withdraw"]},
{s["commandsUntilCooldown"]["deposit"]},
{s["commandsUntilCooldown"]["send"]},
{s["commandsUntilCooldown"]["cockfight"]},
{s["commandsUntilCooldown"]["blackjack"]},
{s["commandsUntilCooldown"]["slots"]},
{s["commandsUntilCooldown"]["buy"]},
{s["cooldowns"]["work"]},
{s["cooldowns"]["crime"]},
{s["cooldowns"]["rob"]},
{s["cooldowns"]["slut"]},
{s["cooldowns"]["beg"]},
{s["cooldowns"]["withdraw"]},
{s["cooldowns"]["deposit"]},
{s["cooldowns"]["send"]},
{s["cooldowns"]["cockfight"]},
{s["cooldowns"]["blackjack"]},
{s["cooldowns"]["slots"]},
{s["cooldowns"]["buy"]},
{s["payouts"]["crime"]["max"]},
{s["payouts"]["crime"]["min"]},
{s["payouts"]["work"]["max"]},
{s["payouts"]["work"]["min"]},
{s["payouts"]["slut"]["max"]},
{s["payouts"]["slut"]["min"]},
{s["failrates"]["crime"]},
{s["failrates"]["rob"]},
{s["failrates"]["slut"]},
{s["fines"]["crime"]["max"]},
{s["fines"]["crime"]["min"]},
{s["fines"]["work"]["max"]},
{s["fines"]["work"]["min"]},
{s["fines"]["slut"]["max"]},
{s["fines"]["slut"]["min"]},
{s["betting"]["max"]},
{s["betting"]["min"]},
{wrapQuotes(s["shop"]["availableItems"])},
{s["shop"]["chicken"]["price"]},
{s["shop"]["chicken"]["max"]},
{s["shop"]["nft"]["price"]},
{s["shop"]["nft"]["max"]},
{s["wallet_max"]},
{s["interest"]},
{s["reply"]},
{s["commandsUntilCooldownResetTime"]},
{wrapQuotes(s["coinname"])},
{s["defaultLeaderboardEntries"]})''')

    def getDiscordUserList(self, guildid):
        self.cursor.execute(f"SELECT * FROM User WHERE guildid={guildid}")
        return [x[1] for x in self.cursor.fetchall()]

    def addUser(self, discorduserid, guildid, s):
        self.execute(f'''
INSERT INTO User(discorduserid,guildid,commandsUntilCooldownRemaining_work,commandsUntilCooldownRemaining_crime,commandsUntilCooldownRemaining_rob,commandsUntilCooldownRemaining_slut,commandsUntilCooldownRemaining_beg,commandsUntilCooldownRemaining_withdraw,commandsUntilCooldownRemaining_deposit,commandsUntilCooldownRemaining_send,commandsUntilCooldownRemaining_cockfight,commandsUntilCooldownRemaining_blackjack,commandsUntilCooldownRemaining_slots,commandsUntilCooldownRemaining_buy,firstCommandExecuted_work,firstCommandExecuted_crime,firstCommandExecuted_rob,firstCommandExecuted_slut,firstCommandExecuted_beg,firstCommandExecuted_withdraw,firstCommandExecuted_deposit,firstCommandExecuted_send,firstCommandExecuted_cockfight,firstCommandExecuted_blackjack,firstCommandExecuted_slots,firstCommandExecuted_buy,cooldowns_work,cooldowns_crime,cooldowns_rob,cooldowns_slut,cooldowns_beg,cooldowns_withdraw,cooldowns_deposit,cooldowns_send,cooldowns_cockfight,cooldowns_blackjack,cooldowns_slots,cooldowns_buy,inventory_chicken,inventory_nft,wallet,bank,winnings,losses) VALUES (
{discorduserid},
{guildid},
{s["commandsUntilCooldownRemaining"]["work"]},
{s["commandsUntilCooldownRemaining"]["crime"]},
{s["commandsUntilCooldownRemaining"]["rob"]},
{s["commandsUntilCooldownRemaining"]["slut"]},
{s["commandsUntilCooldownRemaining"]["beg"]},
{s["commandsUntilCooldownRemaining"]["withdraw"]},
{s["commandsUntilCooldownRemaining"]["deposit"]},
{s["commandsUntilCooldownRemaining"]["send"]},
{s["commandsUntilCooldownRemaining"]["cockfight"]},
{s["commandsUntilCooldownRemaining"]["blackjack"]},
{s["commandsUntilCooldownRemaining"]["slots"]},
{s["commandsUntilCooldownRemaining"]["buy"]},
"{s["firstCommandExecuted"]["work"]}",
"{s["firstCommandExecuted"]["crime"]}",
"{s["firstCommandExecuted"]["rob"]}",
"{s["firstCommandExecuted"]["slut"]}",
"{s["firstCommandExecuted"]["beg"]}",
"{s["firstCommandExecuted"]["withdraw"]}",
"{s["firstCommandExecuted"]["deposit"]}",
"{s["firstCommandExecuted"]["send"]}",
"{s["firstCommandExecuted"]["cockfight"]}",
"{s["firstCommandExecuted"]["blackjack"]}",
"{s["firstCommandExecuted"]["slots"]}",
"{s["firstCommandExecuted"]["buy"]}",
"{s["cooldowns"]["work"]}",
"{s["cooldowns"]["crime"]}",
"{s["cooldowns"]["rob"]}",
"{s["cooldowns"]["slut"]}",
"{s["cooldowns"]["beg"]}",
"{s["cooldowns"]["withdraw"]}",
"{s["cooldowns"]["deposit"]}",
"{s["cooldowns"]["send"]}",
"{s["cooldowns"]["cockfight"]}",
"{s["cooldowns"]["blackjack"]}",
"{s["cooldowns"]["slots"]}",
"{s["cooldowns"]["buy"]}",
"{s["inventory"]["chicken"]}",
"{s["inventory"]["nft"]}",
{s["wallet"]},
{s["bank"]},
{s["winnings"]},
{s["losses"]}
)
''')

    def getUserBalances(self, discorduserid, guildid):
        self.cursor.execute(
            f"SELECT * FROM User WHERE discorduserid={discorduserid} AND guildid={guildid}"
        )
        return [(x[41], x[42]) for x in self.cursor.fetchall()][0]

    def getUserIds(self, guildid):
        self.cursor.execute(f"SELECT * FROM User WHERE guildid={guildid}")
        return [x[1] for x in self.cursor.fetchall()]

    def getGuildSetting(self, guildid, key):
        print(f"SELECT {key} FROM Guild WHERE guildid={guildid}")
        self.cursor.execute(f"SELECT {key} FROM Guild WHERE guildid={guildid}")
        return self.cursor.fetchall()[0][0]

    def setGuildSetting(self, guildid, key, value):
        self.execute(f"UPDATE Guild SET {key}={value} WHERE guildid={guildid}")

    def getUserSetting(self, discorduserid, guildid, key):
        self.cursor.execute(
            f"SELECT {key} FROM User WHERE discorduserid={discorduserid} AND guildid={guildid}"
        )
        return self.cursor.fetchall()[0][0]

    def setUserSetting(self, discorduserid, guildid, key, value):
        self.execute(
            f"UPDATE User SET {key}={value} WHERE discorduserid={discorduserid} AND guildid={guildid}"
        )

    def updateUserBalance(self, discorduserid, guildid, amount, store):
        self.setUserSetting(
            discorduserid, guildid, store,
            self.getUserBalances(discorduserid,
                                 guildid)[0 if store == "wallet" else 1] +
            amount)
