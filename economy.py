from random import randint, choice, seed, randrange
import time

import dataIO

client = None
settings = []
#words = dataIO.loadWords()
#anagram_sessions_timestamps = {}
anagram_sessions = []
payday_register = {}
PAYDAY_TIME = 300 # seconds between each payday
PAYDAY_SOULS = randrange(1,240) # souls received
BET_TIME = 30
def initialize():
        global bank
        bank = dataIO.fileIO("json/economy.json", "load")

def loadHelp():
        global slot_help, economy_exp

        if settings == []: return False #first run

        slot_help = """ Slot machine payouts:
        :two: :two: :six: Bet * 5000
        :four_leaf_clover: :four_leaf_clover: :four_leaf_clover: +1000
        :cherries: :cherries: :cherries: +800
        :two: :six: Bet * 4
        :cherries: :cherries: Bet * 3

        Three symbols: +500
        Two symbols: Bet * 2

        You need an account to play. {0}register one.
        Bet range: 5 - 100
        """.format(settings["PREFIX"])

        economy_exp = """ **Economy. Get rich and have fun with imaginary currency!**

        {0}register - Register an account at the Twentysix bank
        {0}balance - Check your balance
        {0}slot help - Slot machine explanation
        {0}slot [bid] - Play the slot machine
        {0}payday - Type it every {1} seconds to receive some souls.
        """.format(settings["PREFIX"], str(PAYDAY_TIME))

async def checkCommands(message):
        p = settings["PREFIX"]
        cmd = message.content
        user = message.author
        if cmd == p + "balance":
                if accountCheck(user.id):
                        await client.send_message(message.channel, "{} `Your soul memory is: {}`".format(user.mention, str(checkBalance(user.id))))
                else:
                        await client.send_message(message.channel, "{} `Gavlan can't deal if you don't have account. Type !register to open one.`".format(user.mention, str(checkBalance(user.id))))
        elif cmd == p + "register":
                await registerAccount(user, message)
        elif cmd == p + "slot help":
                await client.send_message(message.author, slot_help)
                await client.send_message(message.channel, "{} `Gavlan send instructions to your PM. Gavlan want many souls!`".format(message.author.mention))
        elif cmd.startswith(p + "slot"):
                await slotMachineCheck(message)
        elif cmd == p + "economy":
                await client.send_message(message.author, economy_exp)
                await client.send_message(message.channel, "{} `Gavlan send instructions to your PM. Gavlan want many souls!`".format(message.author.mention))
        elif cmd == p + "challenge":
                #isChallengeOngoing(message)
                pass
        elif cmd == p + "payday":
                await payday(message)

async def registerAccount(user, message):
        if user.id not in bank:
                bank[user.id] = {"name" : user.name, "balance" : 100}
                dataIO.fileIO("json/economy.json", "save", bank)
                await client.send_message(message.channel, "{} `Soul of a Lost Undead traded in. Current balance: {}`".format(user.mention, str(checkBalance(user.id))))
        else:
                await client.send_message(message.channel, "{} `Gavlan already trading with you!`".format(user.mention))

def accountCheck(id):
        if id in bank:
                return True
        else:
                return False

def checkBalance(id):
        if accountCheck(id):
                return bank[id]["balance"]
        else:
                return False

def withdrawMoney(id, amount):
        if accountCheck(id):
                if bank[id]["balance"] >= int(amount):
                        bank[id]["balance"] = bank[id]["balance"] - int(amount)
                        dataIO.fileIO("json/economy.json", "save", bank)
                else:
                        return False
        else:
                return False

def addMoney(id, amount):
        if accountCheck(id):
                bank[id]["balance"] = bank[id]["balance"] + int(amount)
                dataIO.fileIO("json/economy.json", "save", bank)
        else:
                return False

def enoughMoney(id, amount):
        if accountCheck(id):
                if bank[id]["balance"] >= int(amount):
                        return True
                else:
                        return False
        else:
                return False

async def isChallengeOngoing(message): #Work in progress
        global anagram_sessions, anagram_sessions_timestamps
        id = message.channel.id
        for session in anagram_sessions:
                if time.perf_counter() - session.started >= 600:
                        if session.done:
                                anagram_sessions.remove(session)
                                anagram_sessions.append(Anagram(message))
                                return True
                        else:
                                await client.send_message(message.channel, "{} `A challenge is already ongoing.`".format(message.author.mention))
                                return True
                else:
                        await client.send_message(message.channel, "{} `You have to wait 10 minutes before each challenge.`".format(message.author.mention))
                        return True
        anagram_sessions.append(Anagram(message))

async def payday(message):
        id = message.author.id
        if accountCheck(id):
                PAYDAY_SOULS = randint(1,200)
                if id in payday_register:
                        if abs(payday_register[id] - int(time.perf_counter()))  >= PAYDAY_TIME:
                                addMoney(id, PAYDAY_SOULS)
                                payday_register[id] = int(time.perf_counter())
                                await client.send_message(message.channel, "{} `\"Many deal...many thanks! Gah hah!\" Gavlan gives you (+{} souls!) in exchange for your loot`".format(message.author.mention, str(PAYDAY_SOULS)))
                        else:
                                await client.send_message(message.channel, "{} `Gavlan check inventory. Gavlan be ready again in...{} seconds.`".format(message.author.mention, str(PAYDAY_TIME)))
                else:
                        payday_register[id] = int(time.perf_counter())
                        addMoney(id, PAYDAY_SOULS)
                        await client.send_message(message.channel, "{} `Gavlan gives you (+{} souls!) in exchange for your loot`".format(message.author.mention, str(PAYDAY_SOULS)))
        else:
                await client.send_message(message.channel, "{} `You need to open an account with Gavlan to deal with Gavlan. (!economy)`".format(message.author.mention))

###############SLOT##############

async def slotMachineCheck(message):
        p = settings["PREFIX"]
        msg = message.content.split()
        if len(msg) == 2:
                if msg[1].isdigit():
                        bid = int(msg[1])
                        if enoughMoney(message.author.id, bid):
                                if bid > 49 and bid < 1001:
                                        await slotMachine(message, bid)
                                else:
                                        await client.send_message(message.channel, "{} `Soul Bid must be between 50 and 1000.`".format(message.author.mention))
                        else:
                                await client.send_message(message.channel, "{0} `You not enough Souls. Gavlan need more souls first! ({1}economy)`".format(message.author.mention, settings["PREFIX"]))
                else:
                        await client.send_message(message.channel, "{} `".format(message.author.mention) + p + "slot [bid]`")
        else:
                await client.send_message(message.channel, "{} `".format(message.author.mention) + p + "slot [bid]`")

async def slotMachine(message, bid):
        reel_pattern = [":cherries:", ":cookie:", ":two:", ":four_leaf_clover:", ":cyclone:", ":sunflower:", ":six:", ":mushroom:", ":heart:", ":snowflake:"]
        padding_before = [":mushroom:", ":heart:", ":snowflake:"] # padding prevents index errors
        padding_after = [":cherries:", ":cookie:", ":two:"]
        reel = padding_before + reel_pattern + padding_after
        reels = []
        for i in range(0, 3):
                n = randint(3,12)
                reels.append([reel[n - 1], reel[n], reel[n + 1]])
        line = [reels[0][1], reels[1][1], reels[2][1]]

        display_reels = "  " + reels[0][0] + " " + reels[1][0] + " " + reels[2][0] + "\n"
        display_reels += ">" + reels[0][1] + " " + reels[1][1] + " " + reels[2][1] + "\n"
        display_reels += "  " + reels[0][2] + " " + reels[1][2] + " " + reels[2][2] + "\n"

        if line[0] == ":two:" and line[1] == ":two:" and line[2] == ":six:":
                bid = bid * 5000
                test = 1
                await client.send_message(message.channel, "{}{} `226! Nothing can stop your lust for souls. Your bet is multiplied * 5000! {}!` ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == ":four_leaf_clover:" and line[1] == ":four_leaf_clover:" and line[2] == ":four_leaf_clover:":
                bid += 1000
                await client.send_message(message.channel, "{}{} `Three FLC! Gavlan give +1000!` ".format(display_reels, message.author.mention))
        elif line[0] == ":cherries:" and line[1] == ":cherries:" and line[2] == ":cherries:":
                bid += 800
                await client.send_message(message.channel, "{}{} `Three cherries! Gavlan give +800!` ".format(display_reels, message.author.mention))
        elif line[0] == line[1] == line[2]:
                bid += 500
                await client.send_message(message.channel, "{}{} `Three symbols! Gavlan give +500!` ".format(display_reels, message.author.mention))
        elif line[0] == ":two:" and line[1] == ":six:" or line[1] == ":two:" and line[2] == ":six:":
                bid = bid * 4
                await client.send_message(message.channel, "{}{} `26! Gavlan give * 4! {}!` ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == ":cherries:" and line[1] == ":cherries:" or line[1] == ":cherries:" and line[2] == ":cherries:":
                bid = bid * 3
                await client.send_message(message.channel, "{}{} `Two cherries! Gavlan give * 3! {}!` ".format(display_reels, message.author.mention, str(bid)))
        elif line[0] == line[1] or line[1] == line[2]:
                bid = bid * 2
                await client.send_message(message.channel, "{}{} `Two symbols! Gavlan give * 2! {}!` ".format(display_reels, message.author.mention, str(bid)))
#       elif line[0] == ":cherries:" or line[1] == ":cherries:" or line[2] == ":cherries:":
#               await client.send_message(message.channel, "{}{} `Cherries! Your bet is safe!` ".format(display_reels, message.author.mention))
        else:
                await client.send_message(message.channel, "{}{} `Gavlan wheel. Gavlan deal.` ".format(display_reels, message.author.mention))
                withdrawMoney(message.author.id, bid)
                await client.send_message(message.channel, "`Souls left: {}`".format(str(checkBalance(message.author.id))))
                return True
        addMoney(message.author.id, bid)
        await client.send_message(message.channel, "`Current souls: {}`".format(str(checkBalance(message.author.id))))

#######################################

############### ANAGRAM ###############
#                       Work in progress

class Anagram():
        def __init__(self, message):
                self.channel = message.channel
                self.word = choice(words).lower()
                self.anagram = list(self.word)
                shuffle(self.anagram)
                self.anagram = "".join(self.anagram)
                self.started = int(time.perf_counter())
                self.MAX_TIME = 60
                self.done = False

        def checkWord(self, message):
                if time.perf_counter() - self.Atimestamp  <= self.MAX_TIME: 
                        msg = message.content.lower()
                        if msg.find(self.word) != -1:
                                pass
                else:
                        self.gameOver()

        async def gameOver(self):
                self.done = True
                try:
                        await client.send_message(self.channel, "`Anagram session over! No one guessed the word!`")
                except:
                        pass

######################################
