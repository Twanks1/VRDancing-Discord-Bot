import os.path
import datetime 
import random
import re
import math
import io
import json
from enum import Enum

#  pip3 install gspread oauth2client
#  pip3 install --upgrade google-api-python-client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

#  python3 -m pip install -U discord.py
import discord
from discord.ext import commands
from discord.utils import get

#  python3 -m pip install --upgrade Pillow
from PIL import Image, ImageDraw, ImageFont
from image_utils import ImageText

import logging

###########################
def WHITE(str):
    return "```" + str + "```"
def ORANGE(str):
    return "```fix\n" + str + "```"
def CYAN(str):
    return "```yaml\n" + str + "```"
def RED(str):
    return "```diff\n- " + str + "```"

def Lerp(a, b, val):
    if val > 1:
        val = 1
    if val <= 0:
        val = 0
    return (val * b) + ((1 - val) * a)

###########################
######### GLOBALS #########
###########################
gSheet          = None
gVRdancing      = None
gLogger         = None

class Order(Enum):
    Ascending  = 1
    Descending = 2

###########################
######## SETTINGS #########
###########################
class Settings:
    def __init__(self, file):
        self.lockXP         = True   # Whether mods can use all the XP gain commands
        self.maxXPGain      = 40     # max XP which can be added via addBootyXP command
        self.minLenUsername = 3      # min length of username
        self.maxLenUsername = 25     # max length of username
        self.newUserDM      = True   # Send out new user DM
        self.minLenDesc     = 4      # Minimum amount of characters for the user desc
        self.maxLenDesc     = 1000   # Maximun amount of characters for the user desc

        with open(file) as f:
            self.file = json.load(f)

    def XPLocked(self, user):
        return self.lockXP and not user.guild_permissions.administrator

    def ChannelIDRanks(self):
        return self.file['channels']['ranks']

    def ChannelIDRanksUp(self):
        return self.file['channels']['rank_up']

    def ChannelIDIntroduction(self):
        return self.file['channels']['introduction']
        
    def ChannelIDRules(self):
        return self.file['channels']['rules']

    def ChannelIDSelfRoles(self):
        return self.file['channels']['self_roles']

    def ChannelIDSweatSession(self):
        return self.file['channels']['sweatsession']

gSettings = Settings("settings.json")

###########################

BOT_DESCRIPTION = "A wholesome bot for our VRDancing Discord Server!"
CMD_PREFIX      = '$'
GSHEET_FOLDER   = 'gsheet/'
LOG_LEVEL       = logging.INFO
GSHEET_LINK     = "https://docs.google.com/spreadsheets/d/1QFHim9haIidy8sFablM4dBqUtYFuMiRtOTkBxAwDik0/edit#gid=0"
SPLIT_CHAR      = ';'  # Split character for giving sweatsession xp to users e.g. "NAME1;NAME2;NAME3"

ROLE_ADMIN      = 'Admin'
ROLE_MODERATOR  = 'Moderator'
ROLE_FITNESS_INSTRUCTOR = 'Fitness Instructor'

ROLE_SPLIT_RANK_ROLES    = '»»      Rank Roles       ««'
ROLE_SPLIT_SPECIAL_ROLES = '»»      Special Roles     ««'

XP_LOCK_MSG     = "XP gain is currently locked. Contact any admin to ask for unlock."

###########################
####### BOOTY RANKS #######
###########################
RANK_FITNESS_NEWCOMER  = 'Fitness Newcomer'
RANK_FITNESS_CADET     = 'Fitness Cadet'
RANK_FITNESS_ROOKIE    = 'Fitness Rookie'
RANK_FITNESS_MAJOR     = 'Fitness Major'
RANK_FITNESS_OFFICER   = 'Fitness Officer'
RANK_FITNESS_GENERAL   = 'Fitness General'
RANK_FITNESS_CAPTAIN   = 'Fitness Captain'
RANK_FITNESS_COMMANDER = 'Fitness Commander'
RANK_FITNESS_ADMIRAL   = 'Fitness Admiral'
RANK_FITNESS_COMMODORE = 'Fitness Commodore'
RANK_FITNESS_MARSHALL  = 'Fitness Marshall'
RANK_FITNESS_MARSHALL2 = 'Fitness Marshall II'
RANK_FITNESS_MARSHALL3 = 'Fitness Marshall III'
RANK_FITNESS_GOD       = 'Fitness God'

class Rank:
    def __init__(self, name, requiredPoints, color):
        self.name = name
        self.requiredPoints = requiredPoints
        self.color = color

# Define all ranks
gRanks = [
    Rank(RANK_FITNESS_NEWCOMER,  0,     "#ffffff"),
    Rank(RANK_FITNESS_CADET,     10,    "#607d8b"),
    Rank(RANK_FITNESS_ROOKIE,    40,    "#1f8b4c"),
    Rank(RANK_FITNESS_MAJOR,     80,    "#2ecc71"),
    Rank(RANK_FITNESS_OFFICER,   150,   "#206694"),
    Rank(RANK_FITNESS_GENERAL,   250,   "#3498db"),
    Rank(RANK_FITNESS_CAPTAIN,   350,   "#71368a"),
    Rank(RANK_FITNESS_COMMANDER, 500,   "#9b59b6"),
    Rank(RANK_FITNESS_ADMIRAL,   650,   "#a84300"),
    Rank(RANK_FITNESS_COMMODORE, 800,   "#e67e22"),
    Rank(RANK_FITNESS_MARSHALL,  1000,  "#f1c40f"),
    Rank(RANK_FITNESS_MARSHALL2, 2000,  "#f1c40f"),
    Rank(RANK_FITNESS_MARSHALL3, 5000,  "#f1c40f"),
    Rank(RANK_FITNESS_GOD,       10000, "#f1c40f"),
]

def RankIndex(rank: str):
    for i in range(len(gRanks)):
        if gRanks[i].name == rank:
            return i

XP_SWEATSESSION = 10
XP_INSTRUCTOR   = 20
XP_BASIC_VIDEO  = 20
XP_YT_VIDEO     = 40

###############################
def OnFitnessCadet():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_CADET}. The journey just started...")
def OnFitnessRookie():
    return CYAN(f"You're getting into shape! You are now a {RANK_FITNESS_ROOKIE}.")
def OnFitnessMajor():
    return CYAN(f"Well done! Shake that booty!!! You are now a {RANK_FITNESS_MAJOR}.")
def OnFitnessOfficer():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_OFFICER}. Keep hitting it on the dancefloor!")
def OnFitnessGeneral():
    return ORANGE(f"Twerk that booty! You are now a {RANK_FITNESS_GENERAL}.")
def OnFitnessCaptain():
    return ORANGE(f"Damn booty!! Lookin' gooooood! You are now a {RANK_FITNESS_CAPTAIN}.")
def OnFitnessCommander():
    return ORANGE(f"You are now a {RANK_FITNESS_COMMANDER}. Be careful that you're not falling for the Marshall..")
def OnFitnessAdmiral():
    return ORANGE(f"Congratzz! You are now a {RANK_FITNESS_ADMIRAL}. You really did fall for the Marshall, didn't you?")
def OnFitnessCommodore():
    return ORANGE(f"Holy Shit! That's amazing! Your booty is made out of stone! You are now a {RANK_FITNESS_COMMODORE}.")
def OnFitnessMarshall():
    return ORANGE(f"Damn, you did it!!! You are now a {RANK_FITNESS_MARSHALL}. The Fitness Marshall is so proud of you!")
def OnFitnessMarshall2():
    return ORANGE(f"Holy fucking moly... You are now a {RANK_FITNESS_MARSHALL2}.")
def OnFitnessMarshall3():
    return ORANGE(f"What the fucking hell? You are now a {RANK_FITNESS_MARSHALL3}.")
def OnFitnessGod():
    return ORANGE(f"You are literally a god amongst humans. You are now a {RANK_FITNESS_GOD}.")

RankUpDM = {RANK_FITNESS_CADET     : OnFitnessCadet,
           RANK_FITNESS_ROOKIE    : OnFitnessRookie,
           RANK_FITNESS_MAJOR     : OnFitnessMajor,
           RANK_FITNESS_OFFICER   : OnFitnessOfficer,
           RANK_FITNESS_GENERAL   : OnFitnessGeneral,
           RANK_FITNESS_CAPTAIN   : OnFitnessCaptain,
           RANK_FITNESS_COMMANDER : OnFitnessCommander,
           RANK_FITNESS_ADMIRAL   : OnFitnessAdmiral,
           RANK_FITNESS_COMMODORE : OnFitnessCommodore,
           RANK_FITNESS_MARSHALL  : OnFitnessMarshall,
           RANK_FITNESS_MARSHALL2 : OnFitnessMarshall2,
           RANK_FITNESS_MARSHALL3 : OnFitnessMarshall3,
           RANK_FITNESS_GOD       : OnFitnessGod
}

###########################
###########################
###########################
async def OnAddedToServer(user: discord.user):
    # Post message in systems channel
    card = await gVRdancing.GenerateJoinServerCard(user)
    await gVRdancing.guild.system_channel.send(f"{user.mention}", file=card)
    #await message.add_reaction(":fm:")

    # Add roles to new user
    await gVRdancing.AddRoles(user, [RANK_FITNESS_NEWCOMER, ROLE_SPLIT_RANK_ROLES, ROLE_SPLIT_SPECIAL_ROLES])

    # Send out private DM to user
    if (not gSettings.newUserDM):
        return

    introductionChannel = gVRdancing.GetChannel(gSettings.ChannelIDIntroduction())
    rulesChannel = gVRdancing.GetChannel(gSettings.ChannelIDRules())
    selfRoles = gVRdancing.GetChannel(gSettings.ChannelIDSelfRoles())
    dm = f"""Hey {user.mention}! You finally made it! Welcome to our VRDancing Discord Server.
Please read the {introductionChannel.mention} for more information about our server.
Also read and react to the {rulesChannel.mention} to get full access.
Free free to give you some {selfRoles.mention}, so people know a bit about you!

Additionally, how about introducing yourself by setting a custom description?
If you reply to me with '{CMD_PREFIX}setdesc "INTRODUCE YOURSELF"' other people can query it with the {CMD_PREFIX}whois command.
Put everything into double quotes and use Shift+Enter for newlines! (Max {gSettings.maxLenDesc} characters)
Have fun and welcome again to the booty club!
    """
    await user.send(dm)

async def OnAddedToDatabase(user: discord.user):    
    ranksChannel = gVRdancing.GetChannel(gSettings.ChannelIDRanks())
    sweatsessionChannel = gVRdancing.GetChannel(gSettings.ChannelIDSweatSession())
    dm  = f"""
Hi Active Booty!
You have just been added to the official VRDancing database.
From now on you can get booty experience by joining our {sweatsessionChannel.mention} or creating some cool dance videos!
For more information please check the {ranksChannel.mention} channel in our Discord Server.

Your username in the database has been set to your discord username ({user.mention}#{user.discriminator}).
Please change it to your vrchat username with '{CMD_PREFIX}setmyname "MY FANCY NAME"'. You can check your username with '{CMD_PREFIX}myname'!"""

    embed = discord.Embed()
    embed.description = f"[Database]({GSHEET_LINK})"
    await user.send(dm, embed=embed)

###########################
##### DATABASE LAYOUT #####
###########################
# These need to match the name in the GoogleSheet!
DB_ID          = 'ID'
DB_DISCORD_ID  = 'Discord ID'
DB_USERNAME    = 'Username'
DB_BOOTY_XP    = 'Booty XP'
DB_RANK        = 'Rank'
DB_DATE_JOINED = 'Date Joined'
DB_DESCRIPTION = 'User Description'

DB_FIRST_COL       = 'A'
DB_DATE_JOINED_COL = 'F'
DB_LAST_COL        = 'G'

#################################################################       
######################### LOGGING ###############################
#################################################################
class Logger:
    def __init__(self, name, logLevel):
        logger = logging.getLogger('discord')
        logger.setLevel(logLevel)
        handler = logging.FileHandler(filename=name+'.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        logging.basicConfig() # Print logging to console
        self.logger = logger
    
    def Log(self, msg):
        self.logger.log(logging.INFO, msg)

    def Warn(self, msg):
        self.logger.warning(msg)

#################################################################       
##################### DISCORD USER ##############################
#################################################################
class DiscordUser():
    def __init__(self, dcUser, row, id, discordID, username, bootyXP, rank, dateJoined, userDesc):
        self.discordUser = dcUser # Can be None if this class was created as read-only (e.g. for top member query)
        self.row         = int(row)
        self.id          = int(id)
        self.discordID   = int(discordID)
        self.name        = username
        self.bootyXP     = int(bootyXP)
        self.rank        = rank
        self.dateJoined  = dateJoined
        self.userDesc    = userDesc

    async def SetXP(self, val):
        prev = self.bootyXP
        self.bootyXP = val        
        gSheet.DBSetBootyXP(self, self.bootyXP)
        await self.__CheckRank()
        gSheet.SortByColumn(gSheet.dbIndexBootyXP+1, Order.Descending)
        return prev

    def SetUsername(self, name: str):
        prev = self.name
        self.name = name
        gSheet.DBSetUsername(self, self.name)
        return prev

    def SetDescription(self, desc: str):
        self.userDesc = desc
        gSheet.DBSetDescription(self, self.userDesc)

    def GetNextRankName(self):
        return self.__NextRank().name

    def GetNextRankMissingXP(self):
        nextRank = self.__NextRank()
        return nextRank.requiredPoints - self.bootyXP

    # Returns the rank number based on it's booty XP
    def GetRankNumber(self):
        return gSheet.GetMemberRank(self.discordUser)

    async def __CheckRank(self):
        # Figure out which rank we are in
        curRank = gRanks[0]
        for rank in gRanks:
            if self.bootyXP < rank.requiredPoints:
                break
            curRank = rank

        # Check if the rank has changed and update db if necessary
        if self.rank != curRank.name:
            await self.OnRankChanged(curRank.name)
            
    async def OnRankChanged(self, newRank):
        # Update database
        gSheet.DBSetRank(self, newRank)

        # Remove role and add new role
        oldRank = self.rank
        try:
            await gVRdancing.RemoveRole(self.discordUser, oldRank)
        except:
            gLogger.Warn(f"Couldn't remove role {self.rank} from user {self.name} (Does the role exist?)")

        self.rank = newRank
        
        try:
            await gVRdancing.AddRole(self.discordUser, self.rank)        
        except:
            gLogger.Warn(f"Couldn't add role {self.rank} to user {self.name} (Does the role exist?)")

        newRankIndex = RankIndex(newRank)
        if newRankIndex < RankIndex(oldRank):
            return # Skip in case the new rank is lower (e.g. when admin changed the points manually)        

        try:
            # Send DM to user that his rank has changed
            await self.discordUser.send(RankUpDM[newRank]())

            # Send the rank card to the user as DM
            card = await gVRdancing.GenerateRankCard(self.discordUser)
            await self.discordUser.send(file=card)

            channel = gVRdancing.GetChannel(gSettings.ChannelIDRanksUp())            
            card = await gVRdancing.GenerateRankCard(self.discordUser)
            await channel.send(f"{self.discordUser.mention} just achieved a new rank: {self.rank} ({gRanks[newRankIndex].requiredPoints} XP was needed)", file=card)
        except:
            gLogger.Warn("Failed to send a rank up message in the rank up channel (Wrong channel id set?)")
            pass

    def __NextRank(self):
        for rank in gRanks:
            if self.bootyXP < rank.requiredPoints:
                return rank
        return gRanks[-1]
        
    @staticmethod
    def GetNamesOfMembersAsList(members):
        if not members:
            return ""
        names = "["+members[0].name
        for user in members[1:]:
            names += ", " + user.name
        return names + "]"

#################################################################       
######################## VRDANCING ##############################
#################################################################
class VRDancing(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        global gVRdancing
        gVRdancing = self

        intents = discord.Intents.default()
        intents.members = True

        bot = commands.Bot(command_prefix=CMD_PREFIX, description=BOT_DESCRIPTION, intents=intents, case_insensitive=True)
        self.bot = bot

        ######################### COMMANDS ##############################
        @bot.event
        async def on_ready():
            gLogger.Log('Logged in as {0.user}'.format(bot))
            self.guild = self.bot.guilds[0]

        @bot.event
        async def on_member_join(user):
            await OnAddedToServer(user)               

        @bot.event
        async def on_command_error(ctx, error):
             # This prevents any commands with local handlers being handled here in on_command_error.
            if hasattr(ctx.command, 'on_error'):
                return

            # This prevents any cogs with an overwritten cog_command_error being handled here.
            cog = ctx.cog
            if cog:
                if cog._get_overridden_method(cog.cog_command_error) is not None:
                    return

            if isinstance(error, commands.CommandNotFound):
                await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('**Please pass in all requirements.**')
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("**You dont have all the requirements or permissions for using this command.**")
            elif isinstance(error, commands.ArgumentParsingError):
                await ctx.send("**Failed to parse the given arguments.**")
            else:
                await ctx.send("**An unknown error has occured while processing the command. Try using** `help` **to figure out commands!**")

        ####################### ADMIN COMMANDS ############################
        class Admin(commands.Cog):
            """All commands usable by an administrator"""

            async def cog_check(self, ctx):
                admin = get(ctx.guild.roles, name=ROLE_ADMIN)
                return admin in ctx.author.roles or ctx.author.guild_permissions.administrator

            @commands.command(pass_context=True)
            async def DBSetBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """Sets booty experience for users. Usage: cmd @userN value"""
                gLogger.Log(f"{ctx.author.name} changed booty points to {value} for {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = ""
                for user in members:
                    member = await gSheet.GetMember(user)
                    prev = await member.SetXP(value)
                    msg += f"Changed Booty XP for {user.mention}. New XP: {value} (Prev: {prev})\n"   
                await ctx.send(msg)   

            @commands.command(pass_context=True)
            async def DBSubBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """Removes booty experience. Usage: cmd @userN value"""
                gLogger.Log(f"{ctx.author.name} subtracted {value} booty points for {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = ""
                for user in members:
                    member = await gSheet.GetMember(user)
                    newXP = max(0, member.bootyXP - value)
                    await member.SetXP(newXP)
                    msg += f"Subtracted {value} booty points from {user.name}. New XP: {newXP}\n"
                await ctx.send(msg)   

            @commands.command(pass_context=True)
            async def DBDeleteUser(self, ctx, members: commands.Greedy[discord.Member]):
                """Deletes users from the DB. Usage: cmd @userN"""
                gLogger.Log(f"{ctx.author.name} deletes users {DiscordUser.GetNamesOfMembersAsList(members)} in db")
                for user in members:
                    success = gSheet.DBDeleteMember(user)
                    if success:
                        await ctx.send(f"Deleted {user.mention} successfully from DB")
                    else:
                        await ctx.send(f"Could not delete {user.mention} from DB (User doesn't exist)")

            @commands.command(pass_context=True)
            async def DBSortByXP(self, ctx, order: str):
                """Usage: 'DBSortByXP asc' or 'DBSortByXP des'"""
                gSheet.SortByColumn(gSheet.dbIndexBootyXP+1, Order.Ascending if order == "asc" else Order.Descending)
                embed = discord.Embed()
                embed.description = f"[Database]({GSHEET_LINK})"
                await ctx.send("```GSheet was successfully sorted.```", embed=embed)
       
            @commands.command(pass_context=True)
            async def LockXP(self, ctx):
                """Locks the ability to change XP for Mods"""
                gSettings.lockXP = True
                await ctx.send("```XP Gain locked for Mods```")

            @commands.command(pass_context=True)
            async def UnlockXP(self, ctx):
                """Unlocks the ability to change XP for Mods"""
                gSettings.lockXP = False
                await ctx.send("```XP Gain unlocked for Mods```")

            @commands.command(pass_context=True)
            async def FitnessInstructor(self, ctx, newInstructor: discord.Member):
                """Sets a new fitness instructor for the upcoming week"""
                role = get(ctx.guild.roles, name=ROLE_FITNESS_INSTRUCTOR)
                for user in ctx.guild.members:
                    if role in user.roles:
                        await user.remove_roles(role)

                # Add new role to the new instructor
                await gVRdancing.AddRole(newInstructor, ROLE_FITNESS_INSTRUCTOR)
                channel = gVRdancing.GetChannel(gSettings.ChannelIDSweatSession())
                await ctx.send(f"Updated {ROLE_FITNESS_INSTRUCTOR} roles. {newInstructor.mention} You can now post in {channel.mention}. You've also gained {XP_INSTRUCTOR} Booty XP!")

                # Give additional XP for being an instructor
                member = await gSheet.GetMember(newInstructor)
                await member.SetXP(member.bootyXP + XP_INSTRUCTOR)

            
            @commands.command(pass_context=True)
            async def DM(self, ctx, members: commands.Greedy[discord.Member], dm: str):
                """Send a DM from the bot to one or multiples user"""
                for user in members:
                    try:
                        await user.send(dm)
                        await ctx.send(f"DM sent to {user.name}")
                    except:
                        await ctx.send("Failed to send DM to {user.name} (probably due to private settings)")

            @commands.command(pass_context=True)
            async def DMAll(self, ctx, roles: commands.Greedy[discord.Role], dm: str):
                """Sends a DM to all guild-members. CAREFUL! Usage: cmd [@Roles] 'DM'"""
                gLogger.Log(f"{ctx.author.name} broadcasted a DM to all members in the server")

                roleString = ""
                for role in roles[0:-1]:
                    roleString += role.name + "|"  
                roleString += roles[-1].name   

                users = []
                for user in ctx.guild.members:
                    if user.bot:
                        continue # Skip sending message to bots

                    if roles and not all(role in user.roles for role in roles):
                        continue # User don't have all roles

                    users.append(user)

                i = 0
                numMembers = len(users)

                if numMembers == 0:
                    await ctx.send("Sorry, couldn't find anyone to send this to!")
                    return

                for user in users:
                    i = i + 1
                    try:
                        await user.send(dm)
                        await ctx.send(f"DM sent to #{i}/{numMembers}: {user.name}")
                    except:
                        await ctx.send(f"Failed to send DM to #{i}: {user.name} (probably due to private settings)")
                    
                    if not roles:
                        continue # DM sending to everyone without further notice

                    # Let user know which roles got the message
                    try:
                        await user.send(CYAN(f"This message has been sent to all people with following roles: [{roleString}]"))
                    except:
                        pass

                await ctx.send("Done")

            @commands.command(pass_context=True)
            async def AddRoles(self, ctx, members: commands.Greedy[discord.Member], roles: commands.Greedy[discord.Role]):
                """Adds roles to an arbitrary amount of users"""
                for user in members:
                    await user.add_roles(roles)
                await ctx.reply(RED("Roles added"))


            @commands.command(pass_context=True)
            async def RemoveRoles(self, ctx, members: commands.Greedy[discord.Member], roles: commands.Greedy[discord.Role]):
                """Removes roles to an arbitrary amount of users"""
                for user in members:
                    await user.remove_roles(roles)
                await ctx.send(RED("Roles removed"))

        ####################### MOD COMMANDS ############################
        class Moderator(commands.Cog):
            """All commands usable by moderators"""

            async def cog_check(self, ctx):
                mod = get(ctx.guild.roles, name=ROLE_MODERATOR)
                admin = get(ctx.guild.roles, name=ROLE_ADMIN)
                return mod in ctx.author.roles or admin in ctx.author.roles

            @commands.command(pass_context=True)
            async def DBAddBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """@Users VALUE"""
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return

                if (value <= 0 or value > gSettings.maxXPGain):
                    await ctx.reply(f"Value must lie within 1 - {gSettings.maxXPGain}!", mention_author=True)
                    return
                gLogger.Log(f"{ctx.author.name} added {value} booty xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, value)
                await ctx.send(msg)

            @commands.command(pass_context=True)
            async def SweatsessionXP(self, ctx, str: str):
                """Adds booty experience to an arbitrary amount of users based on a given string"""
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return

                missingUsers = []
                foundUsers = []

                # Add XP to every user
                users = str.split(SPLIT_CHAR)                
                for user in users:
                    member = await gSheet.GetMemberByName(user)
                    if not member:
                        missingUsers.append(user)
                        continue
                    foundUsers.append(user)
                    await ctx.send(f"Adding {XP_SWEATSESSION} booty xp to '{member.name}'...")
                    await member.SetXP(member.bootyXP + XP_SWEATSESSION)                    

                gLogger.Log(f"{ctx.author.name} added {XP_SWEATSESSION} booty xp to {foundUsers}")

                msg = f"Added {XP_SWEATSESSION} XP to {foundUsers}."
                if not missingUsers:
                    await ctx.send(msg)
                else:
                    foundUserMsg = msg+'\n' if foundUsers else ""
                    await ctx.send(f"{foundUserMsg}Couldn't find these members: {missingUsers} (Wrong name or they left the guild)")


            @commands.command(pass_context=True)
            async def GiveSweatsessionXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience worth of a sweatsession. Usage: cmd @user"""
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return
                gLogger.Log(f"{ctx.author.name} added sweatsession xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, XP_SWEATSESSION)
                await ctx.send(msg)

            @commands.command(pass_context=True)
            async def GiveVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience worth of a basic dance video. Usage: cmd @user"""
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return
                gLogger.Log(f"{ctx.author.name} added basic video xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, XP_BASIC_VIDEO)
                await ctx.send(msg)

            @commands.command(pass_context=True)
            async def GiveYoutubeVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience worth of a YouTube video for VRDancing. Usage: cmd @user"""
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return
                gLogger.Log(f"{ctx.author.name} added YT video xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, XP_YT_VIDEO)
                await ctx.send(msg)
                

            async def __AddBootyXP(self, members, val):
                msg = ""
                for user in members:
                    member = await gSheet.GetMember(user)
                    newXP = member.bootyXP + val
                    await member.SetXP(newXP)
                    msg += f"Added {val} booty points to {user.mention}. New XP: {newXP}\n"
                return msg
            
        ####################### USER COMMANDS ############################
        class User(commands.Cog):
            """All commands usable by any user"""
                
            async def cog_check(self, ctx):
                return True

            @commands.command(pass_context=True)
            async def Rank(self, ctx, members: commands.Greedy[discord.Member]):
                """Shows a rank. If no argument is provided it shows your rank."""
                 # Display your own rank if no argument was provided
                if not members:
                    if len(ctx.view.buffer) > len("$rank"):
                        await ctx.reply("Invalid arguments provided. Either ping a member with @ or use no argument to show your rank.", mention_author=True)
                        return
                    card = await gVRdancing.GenerateRankCard(ctx.author)
                    await ctx.send(file=card)

                # Display rank of all given users
                for user in members:
                    card = await gVRdancing.GenerateRankCard(user)
                    await ctx.send(file=card)

            @commands.command(pass_context=True, hidden=True)
            async def Chatmans(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://imgur.com/a/CMmabf6')

            @commands.command(pass_context=True, hidden=True)
            async def Kanami(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://imgur.com/a/yQX0GO0')

            @commands.command(pass_context=True, hidden=True)
            async def Cinte(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://imgur.com/a/hYdTbY6')

            @commands.command(pass_context=True, hidden=True)
            async def MiniGreen(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://imgur.com/a/TxluDit')

            @commands.command(pass_context=True, hidden=True)
            async def Raestar(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://media.giphy.com/media/IcCd2FhIzuIo0/giphy.gif')

            @commands.command(pass_context=True)
            async def Ranks(self, ctx):
                """Links the #rank channel"""
                channel = gVRdancing.GetChannel(gSettings.ChannelIDRanks())
                await ctx.send(f"Checkout the {channel.mention} channel for more information.")

            @commands.command(pass_context=True)
            async def SetMyName(self, ctx, name: str):
                """Changes your personal username in the database"""
                gLogger.Log(f"{ctx.author.name} changed his name to {name}")
                if (len(name) < gSettings.minLenUsername):
                    await ctx.reply(f"Username too short. Name must be between {gSettings.minLenUsername} and {gSettings.maxLenUsername} letters.", mention_author=True)
                    return
                if (len(name) > gSettings.maxLenUsername):
                    await ctx.reply(f"Username too long. Name must be between {gSettings.minLenUsername} and {gSettings.maxLenUsername} letters.", mention_author=True)
                    return
                if (gSheet.HasUsername(name)):
                    await ctx.reply(f"Username already taken. Please chooser another one.", mention_author=True)
                    return
                member = await gSheet.GetMember(ctx.author)
                member.SetUsername(name)
                await ctx.reply(f"Username was changed to '{name}''. Please make sure this is your vrchat username (case sensitive!)", mention_author=True)

            @commands.command(pass_context=True)
            async def MyName(self, ctx):
                """Get some information about yourself"""
                member = await gSheet.GetMember(ctx.author)
                await ctx.reply(f"Hi! Your username in the database is currently set to '{member.name}'", mention_author=True)

            @commands.command(pass_context=True)
            async def Highscores(self, ctx):
                """Display's a Highscore list for the top 10 members"""
                highscoreList = gSheet.GetTopMembers(10)

                longestName = 1
                for member in highscoreList:
                    longestName = max(longestName, len(member.name))

                msg = "```"
                for i in  range(len(highscoreList)):
                    member = highscoreList[i]
                    adjustedName = member.name.ljust(longestName)
                    msg += f"{i+1}: {adjustedName} with {member.bootyXP:4} booty XP. ({member.rank})\n" 
                
                embed = discord.Embed()
                embed.description = f"Goto [Database]({GSHEET_LINK}) to see the whole list."
                await ctx.send(f"{msg}```", embed = embed)

            @commands.command(pass_context=True)
            async def SetDesc(self, ctx, desc: str):
                """Introduce yourself by setting a custom description which you can query with the 'whois' command! Execute the command without args to see the limit."""
                if len(desc) < gSettings.minLenDesc:
                    await ctx.reply(f"Description too short. Character amount must lie between {gSettings.minLenDesc} and {gSettings.maxLenDesc}! Also don't forget to put everything into ''!")
                    return;
                if len(desc) > gSettings.maxLenDesc:
                    await ctx.reply(f"Description too long. Character amount must lie between {gSettings.minLenDesc} and {gSettings.maxLenDesc}!")
                    return;

                gLogger.Log(f"{ctx.author.name} updated his description")
                member = await gSheet.GetMember(ctx.author)
                member.SetDescription(desc)
                await ctx.reply(f"```Description sucessfully changed. You can check by using the '{CMD_PREFIX}whois' command without any arguments!```", mention_author=True)

            @commands.command(pass_context=True)
            async def WhoIs(self, ctx, user: discord.Member = None):
                """Returns a custom set message from a any user. Change it with the 'setdesc' command!"""
                if (user is None):
                    user = ctx.author

                card = await gVRdancing.GenerateDescCard(user)  
                await ctx.send(file=card)
                #member = await gSheet.GetMember(user)
                #await ctx.send(f"```{member.name}:\n{member.userDesc}```", mention_author=True)

            @WhoIs.error
            async def whois_error(self, ctx, error):
                await ctx.send(f"```Member doesn't exist in the database...```")

            @commands.command(pass_context=True, hidden=True)
            async def FM(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://cdn.discordapp.com/attachments/793977209642811393/831637815488938014/thing1.gif')

            @commands.command(pass_context=True)
            async def Database(self, ctx):
                """Link to the database"""
                embed = discord.Embed()
                embed.description = f"[Database]({GSHEET_LINK})"
                await ctx.send(embed=embed)

            #@commands.command(pass_context=True)
            #async def Test(self, ctx):
             #   """EASTER EGG"""
              #  message = await ctx.send('TEST')
               # await message.add_reaction('<:fm:831987792833544242>')
                #await message.add_reaction('✅')

            #@commands.Cog.listener()
            #async def on_raw_reaction_add(self, ctx):
                #if ctx.member.bot:
                #    return

                #member = await gSheet.GetMember(ctx.member)
                #await member.SetXP(member.bootyXP + XP_SWEATSESSION)

                #guild = self.bot.get_guild(ctx.guild_id)
                #role = discord.utils.get(guild.roles, name="Verified")
                #await ctx.member.add_roles(role, reason="Verified Self", atomic=True)

        ######################## RUN BOT ################################
        bot.add_cog(Admin())
        bot.add_cog(Moderator())
        bot.add_cog(User())
        token = open('discord/vrdancing.token').read()
        bot.run(token)

    ##################### Public Functions ##########################
    async def RemoveRole(self, user: discord.Member, roleNameOrId):
        try:
            role = self.GetRole(roleNameOrId)
            await user.remove_roles(role)
        except:
            gLogger.Warn(f"Failed to remove role [{roleNameOrId}] to {user.name} (Role doesn't exist?)")

    async def AddRole(self, user: discord.Member, roleNameOrId):
        try:
            role = self.GetRole(roleNameOrId)
            await user.add_roles(role)
        except:
            gLogger.Warn(f"Failed to add role [{roleNameOrId}] to {user.name} (Role doesn't exist?)")

    async def AddRoles(self, user: discord.Member, roles):
        for role in roles:
            await self.AddRole(user, role)        

    def GetRole(self, roleNameOrId):
        if isinstance(roleNameOrId, str):
            return get(self.guild.roles, name=roleNameOrId)
        else:
            return get(self.guild.roles, id=roleNameOrId)

    def GetChannel(self, id):
        return self.guild.get_channel(id)

    async def GenerateRankCard(self, user: discord.Member):
        member = await gSheet.GetMember(user)

        currentRankIndex = RankIndex(member.rank)
        bMaxLevel = currentRankIndex == len(gRanks)-1

        rankCur  = gRanks[currentRankIndex]
        rankNext = gRanks[min(currentRankIndex + 1, len(gRanks)-1)]

        username       = member.name                    
        currentXP      = member.bootyXP
        currentRank    = rankCur.name
        nextRank       = rankNext.name
        XPCurrentLevel = rankCur.requiredPoints
        XPNextLevel    = rankNext.requiredPoints                    
        rankColor      = rankCur.color
        nextRankColor  = rankNext.color
            
        # Image
        w, h = 1024, 256
        img = Image.new("RGBA", (w, h), "#090A0B")
        draw = ImageDraw.Draw(img)            

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        # Progress Bar
        progressBarStart = (286, 180)
        progressBarEnd = (984, 230)
        progressBarHeight = progressBarEnd[1] - progressBarStart[1]
        draw.rectangle([progressBarStart,progressBarEnd], fill=(72, 75, 78))
        percentageToNextLevel = 1 if bMaxLevel else (currentXP - XPCurrentLevel)/(XPNextLevel - XPCurrentLevel)
        if percentageToNextLevel > 0:
            draw.rectangle([progressBarStart, (progressBarStart[0] + percentageToNextLevel*(progressBarEnd[0]-progressBarStart[0]), progressBarEnd[1])], fill=rankColor) 

        textAboveProgressBarY = progressBarStart[1] - 20
        textAboveProgressBarMargin = 25

        # Rank
        fontPathForText = "fonts/CutieShark.ttf"
        fnt = ImageFont.truetype(fontPathForText, 70)
        strRank = f"{currentRank}"
        sw, sh = draw.textsize(strRank, fnt)
        rankTextY = sh
        draw.text((w - 20, rankTextY), strRank, font=fnt, fill=rankColor, align="right", anchor="rs")

        fnt = ImageFont.truetype(fontPathForText, 40)
        draw.text((w - 50 - sw, rankTextY), f"Rank #{member.GetRankNumber()}", font=fnt, fill="#6C7071", align="right", anchor="rs")

        # Username
        usernameLenMaxPercent = len(username) / gSettings.maxLenUsername
        usernameFontSize = int(Lerp(25, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
        fnt = ImageFont.truetype("fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf", usernameFontSize) # Unicode font which contains special characters like ღὣ
        draw.text((progressBarStart[0] + textAboveProgressBarMargin, textAboveProgressBarY), f"{username}", font=fnt, fill=rankColor, anchor="ls")

        # XP
        fnt = ImageFont.truetype(fontPathForText, 30)
        bootyXPStr = f"/ {XPNextLevel} Booty XP"
        draw.text((progressBarEnd[0] - textAboveProgressBarMargin, textAboveProgressBarY), bootyXPStr, font=fnt, fill="#6C7071", align="right", anchor="rs")
        
        sw, sh = draw.textsize(bootyXPStr, fnt)
        draw.text((progressBarEnd[0] - textAboveProgressBarMargin - sw - 10, textAboveProgressBarY), f"{currentXP}", font=fnt, fill="#FFFFFF", align="right", anchor="rs")

        # Next Rank
        fnt = ImageFont.truetype(fontPathForText, 40)
        draw.text((progressBarEnd[0] - 10, progressBarEnd[1] - progressBarHeight/2), f"{nextRank}", font=fnt, fill=nextRankColor, align="right", anchor="rm")

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")

    async def GenerateDescCard(self, user: discord.Member):
        member = await gSheet.GetMember(user)

        # creating Image object
        w, h = 1024, 256
        img = ImageText((w, h), background="#090A0B")                  

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        currentRankIndex = RankIndex(member.rank)

        rankCur  = gRanks[currentRankIndex]
        rankNext = gRanks[min(currentRankIndex + 1, len(gRanks)-1)]

        username    = member.name
        currentRank = rankCur.name                  
        rankColor   = rankCur.color

        x = 280
        usernameFont = "fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf"

        # Username
        y = 60
        usernameLenMaxPercent = len(username) / gSettings.maxLenUsername
        usernameFontSize = int(Lerp(30, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
        img.write_text(x, y, text=username, font_filename=usernameFont, font_size=usernameFontSize, color=rankColor, anchor="lb")

        # Rank
        fontRank = "fonts/CutieShark.ttf"
        img.write_text(1024 - 10, 35, text=currentRank, font_filename=fontRank, font_size="fill", max_height=35, color=rankColor, anchor="rs")

        # Joined the server date
        try:
            dateJoined = user.joined_at.strftime("%d.%m.%Y")
            img.write_text(1024 - 10, 55, text=f"Joined {dateJoined}", font_filename=fontRank, font_size="fill", max_height=20, color="#6C7071", anchor="rs")
        except:
            pass # Command was called in private bot dm so no join date exists

        # Description
        y = y + 8
        rightMargin = 15
        bottomMargin = 10
        boxWidth = w - x - rightMargin
        boxHeight = h - y - bottomMargin    
        descriptionFont = "fonts/seguiemj.ttf"
        img.write_text_box_fit(x, y, text=member.userDesc, box_width=boxWidth, box_height=boxHeight, max_font_size = 30, font_filename=descriptionFont, color="#2FD0AA", embedded_color=True)

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")

    ##############################################
    async def GenerateJoinServerCard(self, user: discord.Member):
        # creating Image object
        w, h = 1024, 256
        img = Image.new("RGBA", (w, h), "#090A0B")
        draw = ImageDraw.Draw(img)                    

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        username = user.name
        discriminator = f"#{user.discriminator}"

        x, y = 350, 128

        # Username
        fnt = ImageFont.truetype("fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf", 80) # Unicode font which contains special characters like ღὣ
        draw.text((x, y), username, font=fnt, fill="#D0AA2F", align="right", anchor="ls")

        sw, sh = draw.textsize(username, fnt)
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 40) # Unicode font which contains special characters like ღὣ
        draw.text((x + sw, y), discriminator, font=fnt, fill="#6C7071", anchor="ls")

        # Has joined the server text
        textY = y + 45
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 25)
        strJoined = f"has joined the Booty Army. You are booty "
        draw.text((x, textY), strJoined, font=fnt, fill="#2FD0AA", anchor="ls")

        # Nth booty member
        sw, sh = draw.textsize(strJoined, fnt)
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 45)
        strJoined = f"#{len(gVRdancing.guild.members)}"
        draw.text((x + sw, textY), strJoined, font=fnt, fill="#AA2FD0", anchor="ls")

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")

#################################################################       
######################## GoogleSheet ############################
#################################################################
class GoogleSpreadSheet:
    def __init__(self, spreadSheetName, keysPath):
        scopes = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets', 
         "https://www.googleapis.com/auth/drive.file", 
         "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(keysPath, scopes)
        client = gspread.authorize(creds)
        self.spreadSheet = client.open(spreadSheetName)
        self.spreadSheetName = spreadSheetName
        self.database = self.spreadSheet.worksheet("Database")

        self.dbIndexID         = self.GetColumnIndex(DB_ID)
        self.dbIndexDiscordID  = self.GetColumnIndex(DB_DISCORD_ID)
        self.dbIndexUserName   = self.GetColumnIndex(DB_USERNAME)
        self.dbIndexBootyXP    = self.GetColumnIndex(DB_BOOTY_XP)
        self.dbIndexRank       = self.GetColumnIndex(DB_RANK)
        self.dbIndexDateJoined = self.GetColumnIndex(DB_DATE_JOINED)
        self.dbIndexUserDesc   = self.GetColumnIndex(DB_DESCRIPTION)
        gLogger.Log("Initialized Goggle Spread Sheet: " + spreadSheetName)
    
    def SortByColumn(self, columnIndex: int, order: Order):
        self.database.sort((columnIndex, 'asc' if order == Order.Ascending else 'des'))

    #################################################################       
    ###################### DATABASE READS ###########################
    #################################################################

    def PrintAllRows(self, sheetName):
        sheet = self.spreadSheet.worksheet(sheetName)
        result = sheet.get_all_records()
        for row in result:
            print(row)

    def GetAllRows(self, sheetName):
        sheet = self.spreadSheet.worksheet(sheetName)
        result = sheet.get_all_records()
        return result

    # Returns a DiscordMember(), creates a new one in the DB if it doesn't exist yet
    async def GetMember(self, user: discord.user):
        if user.bot:
            return None

        try:
            result = self.database.find(str(user.id), in_column=self.dbIndexDiscordID+1)
        except:
            self.DBCreateNewMember(user)
            result = self.database.find(str(user.id), in_column=self.dbIndexDiscordID+1)     
            await OnAddedToDatabase(user)

        row = self.database.row_values(result.row)

        return DiscordUser(user, result.row, row[self.dbIndexID], row[self.dbIndexDiscordID], row[self.dbIndexUserName], 
        row[self.dbIndexBootyXP], row[self.dbIndexRank], row[self.dbIndexDateJoined], row[self.dbIndexUserDesc])

    
    # Returns a DiscordMember(), None if the user didn't exist
    async def GetMemberByName(self, user: str):
        try:
            result = self.database.find(user, in_column=self.dbIndexUserName+1)
        except:            
            return None

        row = self.database.row_values(result.row)

        discordIdAsInt = int(row[self.dbIndexDiscordID])
        try:
            dcUser = await gVRdancing.guild.fetch_member(discordIdAsInt)
        except:
            return None # User was in database but is no longer part of the guild

        return DiscordUser(dcUser, result.row, row[self.dbIndexID], row[self.dbIndexDiscordID], row[self.dbIndexUserName], 
        row[self.dbIndexBootyXP], row[self.dbIndexRank], row[self.dbIndexDateJoined], row[self.dbIndexUserDesc])

    # Return: Column index for a given name
    def GetColumnIndex(self, columnName):
        try:
            row = self.database.row_values(1)
            return row.index(columnName)
        except:
            gLogger.Warn(f"Could not find index for column '{columnName}'")
            return -1

    def HasMember(self, user: discord.user):
        try:
            self.database.find(str(user.id), in_column=self.dbIndexDiscordID+1)
            return True
        except:
            return False

    def HasUsername(self, name: str):
        try:
            self.database.find(name, in_column=self.dbIndexUserName+1)
            return True
        except:
            return False

    # Returns the rank number of a user based on it's booty xp
    def GetMemberRank(self, user: discord.user):
        # Get column with booty XP and figure out best N members
        colXP = self.database.col_values(self.dbIndexBootyXP+1)
        valsXP = list(map(int, colXP[1:])) # Cut of header from list
        colDiscordID = self.database.col_values(self.dbIndexDiscordID+1)
        valsDiscordID = list(map(int, colDiscordID[1:])) # Cut of header from list

        # Add the index to each entry, sort and return the index of the users discord id
        sortedVals = []
        for i in range(len(valsXP)):
            sortedVals.append((valsDiscordID[i], valsXP[i]))
        sortedVals.sort(key=lambda x: x[1], reverse=True) # Max elements at front of the list
        return [x[0] for x in sortedVals].index(user.id) + 1

    def GetTopMembers(self, n: int):
        # Get column with booty XP and figure out best N members
        col = self.database.col_values(self.dbIndexBootyXP+1)
        vals = list(map(int, col[1:])) # Cut of header from list

        sortedVals = []
        for i in range(len(vals)):
            sortedVals.append((i + 2, vals[i]))

        sortedVals.sort(key=lambda x: x[1], reverse=True) # Max elements at front of the list
        ranges = []
        for tup in sortedVals[0:n]:
            row = tup[0]
            ranges.append(f'{DB_FIRST_COL}{row}:{DB_DATE_JOINED_COL}{row}') # Don't query for user desc (can be a lot of data)

        rows = self.database.batch_get(ranges)

        members = []
        for i in range(len(rows)):
            row = rows[i][0]
            members.append(DiscordUser(None, i, row[self.dbIndexID], row[self.dbIndexDiscordID], row[self.dbIndexUserName], 
        row[self.dbIndexBootyXP], row[self.dbIndexRank], row[self.dbIndexDateJoined], "NO DESC QUERIED"))

        return members


    #################################################################       
    ###################### DATABASE WRITES ##########################
    #################################################################
    # Creates a new member in the DB
    def DBCreateNewMember(self, user: discord.user):
        name = f"{user.name}#{user.discriminator}"
        if (self.HasMember(user) or self.HasUsername(name)):
            gLogger.Warn(f"Trying to create member '{user.name}' (Discord id: {user.id}) which already exists!")
            return

        gLogger.Log(f"Creating new member {user.name} (Discord id: {user.id})")

        # Get new ID
        col = self.database.col_values(self.dbIndexID+1)
        ids = list(map(int, col[1:])) # Cut of 'ID' from list
        newID = 1 if not ids else max(ids) + 1

        # Update Sheet
        indexRow = len(col) + 1 # cols start at 1, so add 1
        row = self.database.range(f'{DB_FIRST_COL}{indexRow}:{DB_LAST_COL}{indexRow}')

        row[self.dbIndexID].value         = str(newID)
        row[self.dbIndexDiscordID].value  = str(user.id)
        row[self.dbIndexUserName].value   = name
        row[self.dbIndexBootyXP].value    = 0
        row[self.dbIndexRank].value       = RANK_FITNESS_NEWCOMER
        row[self.dbIndexDateJoined].value = datetime.datetime.now().strftime("%d.%m.%Y")
        row[self.dbIndexUserDesc].value   = f"Your awesome custom description. (Change me with '{CMD_PREFIX}setdesc')"

        self.database.update_cells(row)


    # Deletes a member from the DB (effectively deletes the row)
    def DBDeleteMember(self, user: discord.user):
        ids = self.database.col_values(self.dbIndexDiscordID+1)
        try:
            index = ids.index(str(user.id))
        except:
            gLogger.Warn(f"Could not delete user {user.name} (ID: {user.id}). Reason: User doesn't exist")
            return False

        gLogger.Log(f"Deleting member {user.name} (Discord id: {user.id})")
        indexRow = index + 1
        self.database.delete_rows(indexRow)
        return True

    ######################## PRIVATE FUNCTIONS FOR DISCORD USER ###########################
    def DBSetBootyXP(self, discordUser, val):
        self.database.update_cell(discordUser.row, self.dbIndexBootyXP+1, val)

    def DBSetRank(self, discordUser, val):
        self.database.update_cell(discordUser.row, self.dbIndexRank+1, val)

    def DBSetUsername(self, discordUser, newName: str):
        self.database.update_cell(discordUser.row, self.dbIndexUserName+1, newName)

    def DBSetDescription(self, discordUser, newDesc: str):
        self.database.update_cell(discordUser.row, self.dbIndexUserDesc+1, newDesc)

    #############################################
    def Test(self, sheetName):
        sheet = self.spreadSheet.worksheet(sheetName)

        #highscoreList = gSheet.GetTopMembers(10)

        #result_col = sheet.col_values(1) #See individual column
        #result_cell = sheet.cell(1, 1) # See particular cell

        #sheet.update_cell(2,1,'42')  #Change value
        #sheet.update_cell(2,1,'0')  #Change value

        print('Test done')

##############################################
def TestRankCard():
    # creating Image object
    w, h = 1024, 256
    img = Image.new("RGBA", (w, h), "#090A0B")
    draw = ImageDraw.Draw(img)                    

    # Avatar image
    avatarImage = Image.open("me.png").convert("RGBA")
    avatarImage = avatarImage.resize((256, 256))
    img.alpha_composite(avatarImage)

    username       = f"Chatmans"
    currentRank    = "Fitness Newcomer"
    nextRank       = "Fitness Cadet"
    currentXP      = 170
    XPCurrentLevel = 0
    XPNextLevel    = 1000
    percentageToNextLevel = (currentXP - XPCurrentLevel)/(XPNextLevel - XPCurrentLevel)
    rankColor     = "#F27D07"
    nextRankColor = "#44B37FAA"

    # Progress Bar
    progressBarStart = (286, 180)
    progressBarEnd = (984, 230)
    progressBarHeight = progressBarEnd[1] - progressBarStart[1]
    draw.rectangle([progressBarStart,progressBarEnd], fill=(72, 75, 78))
    if percentageToNextLevel > 0:
        draw.rectangle([progressBarStart, (progressBarStart[0] + percentageToNextLevel*(progressBarEnd[0]-progressBarStart[0]), progressBarEnd[1])], fill=rankColor) 

    textAboveProgressBarY = progressBarStart[1] - 20
    textAboveProgressBarMargin = 25

    # Rank
    fnt = ImageFont.truetype("fonts/CutieShark.ttf", 60, layout_engine=ImageFont.LAYOUT_RAQM)
    strRank = f"{currentRank}"
    sw, sh = draw.textsize(strRank, fnt)
    draw.text((w - 15, sh), strRank, font=fnt, fill=rankColor, align="right", anchor="rs")

    fnt = ImageFont.truetype("fonts/CutieShark.ttf", 40)
    draw.text((w - 40 - sw, sh), f"Rank #1000", font=fnt, fill="#6C7071", align="right", anchor="rs")

    # Username
    usernameLenMaxPercent = len(username) / gSettings.maxLenUsername
    usernameFontSize = int(Lerp(25, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
    fnt = ImageFont.truetype("fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf", usernameFontSize) # Unicode font which contains special characters like ღὣ
    draw.text((progressBarStart[0] + textAboveProgressBarMargin, textAboveProgressBarY), username, font=fnt, fill="#FFFFFF", anchor="ls")

    # XP
    fnt = ImageFont.truetype("fonts/CutieShark.ttf", 30)
    bootyXPStr = f"/ {XPNextLevel} Booty XP"
    draw.text((progressBarEnd[0] - textAboveProgressBarMargin, textAboveProgressBarY), bootyXPStr, font=fnt, fill="#6C7071", align="right", anchor="rs")
    
    sw, sh = draw.textsize(bootyXPStr, fnt)
    draw.text((progressBarEnd[0] - textAboveProgressBarMargin - sw - 5, textAboveProgressBarY), f"{currentXP}", font=fnt, fill="#FFFFFF", align="right", anchor="rs")

    # Next Rank
    fnt = ImageFont.truetype("fonts/Business-Signature.otf", 40)
    draw.text((progressBarEnd[0] - 10, progressBarEnd[1] - progressBarHeight/2), f"{nextRank}", font=fnt, fill=nextRankColor, align="right", anchor="rm")

    img.show()


##############################################
def TestDescCard():
    # creating Image object
    w, h = 1024, 256
    img = ImageText((w, h), background="#090A0B")                  

    # Avatar image
    avatarImage = Image.open("me.png").convert("RGBA")
    avatarImage = avatarImage.resize((256, 256))
    img.alpha_composite(avatarImage)

    username = f"Silvan"
    username2 = f"The Demon On Welfare"
    username3 = f"WWWWWWWWWWWWWWWWWWWWWWWW"
    number = f"#6666"
    rank = f"Fitness Newcomer"

    x = 280
    usernameFont = "fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf"

    # Username
    y = 60
    usernameLenMaxPercent = len(username) / gSettings.maxLenUsername
    usernameFontSize = int(Lerp(30, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
    img.write_text(x, y, text=username, font_filename=usernameFont, font_size=usernameFontSize, color="#D0AA2F", anchor="lb")

    # Rank
    fontRank = "fonts/CutieShark.ttf"
    img.write_text(1024 - 10, 35, text=rank, font_filename=fontRank, font_size="fill", max_height=35, color="#D0AA2F", anchor="rs")

    # Joined the server date
    str = datetime.datetime.now().strftime("%d.%m.%Y")
    img.write_text(1024 - 10, 55, text=f"Joined: {str}", font_filename=fontRank, font_size="fill", max_height=20, color="#6C7071", anchor="rs")

    # Description
    strDesc = f"Hey, my name is Silvanღὣ.💯🔞🚀👌💯 And this is a very long text, which needs to be multilined.\nI'm the original founder of the VRDancing discord."
    LongTextTest = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas a tortor at mauris volutpat condimentum at sit amet nulla. 💯🔞🚀👌💯 Cras ut sapien vel ipsum auctor porta et at nibh. Nam sollicitudin iaculis lectus et ullamcorper. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus orci est, maximus et nunc vitae, dapibus tristique mauris. Phasellus eu mattis mauris. Etiam eleifend, erat vel varius vehicula, eros odio faucibus quam, eu ullamcorper dui mi id quam. Phasellus iaculis vestibulum mauris, a volutpat sem dignissim commodo. Fusce purus orci, sollicitudin vel pharetra id, aliquet a mi. Fusce vitae varius erat. Donec sit amet augue non tortor euismod condimentum vitae ut sem. Integer ullamcorper diam sit amet dui mollis vulputate. Phasellus nunc quam, feugiat sit amet nulla eu, tempor rutrum elit. Praesent aliquet eros id lectus euismod, sed rutrum lacus scelerisque. Integer sodales nec nisi vitae hendrerit. Etiam est arcu, accumsan mattis."
    EmojiText = "💯🔞🚀👌💯"
    myDesc = "Hi! 💯 I'm Silvan from Germany and born in 1993. I'm the original founder of the VRDancing discord server. Everything began when i first met the Fitness Marshall in PyPy's Just Dance world. Since then i've been dancing for over a year now to him and the fun never stopped. I have improved physically as well as mentally massively and i want to bring this to other people as well. Welcome to the Cult! "
    
    y = y + 8
    rightMargin = 15
    bottomMargin = 10
    boxWidth = w - x - rightMargin
    boxHeight = h - y - bottomMargin    
    descriptionFont = "fonts/seguiemj.ttf"
    img.write_text_box_fit(x, y, text=myDesc, box_width=boxWidth, box_height=boxHeight, max_font_size = 30, font_filename=descriptionFont, color="#2FD0AA", embedded_color=True)

    img.show()

##############################################
def DumpJSON():
    dict = {
        "channels":
            {
                "rank_up" : 827617550325907456,
                "ranks" : 827645739366481930,
                "introduction" : 830858802277777438,
                "self_roles" : 830858814403379200,
                "sweatsession" : 830885430492135424
            }
        ,
    }

    with open('settings.json', 'w') as json_file:
        json.dump(dict, json_file)

##############################################
def TestEmoji(font):
    fnt = ImageFont.truetype("fonts/seguiemj.ttf", size=109, layout_engine=ImageFont.LAYOUT_RAQM)
    im = Image.new("RGBA", (600, 600), (100, 100, 100, 100))
    draw = ImageDraw.Draw(im)
    draw.text((0, 32), "a\u263A", fill="#faa2", embedded_color=True, font=fnt)
    draw.text((0, 132), "a\u263A", fill="#faa8", embedded_color=True, font=fnt)
    draw.text((0, 232), "Test 12345 asgagag", fill="#faa", embedded_color=True, font=fnt)
    draw.text((0, 332), "\U0001F3AC\U0001F44B\U0001F3FB\U0001F44B\U0001F3FF", fill="white", embedded_color=True, font=fnt)
    draw.text((0, 432), "a\u263A", fill="#faa2", font=fnt)
    im.show()

#################################################################       
############################ MAIN ###############################
#################################################################
def main():
    global gSheet
    global gLogger

    #TestRankCard()
    #TestDescCard()

    gLogger = Logger('vrdancing', LOG_LEVEL)

    gSheet = GoogleSpreadSheet('VRDancing',  GSHEET_FOLDER + 'vrdancing_keys.json')
    #gSheet.Test('Database')

    VRDancing()

if __name__ == "__main__":
    main()














    
