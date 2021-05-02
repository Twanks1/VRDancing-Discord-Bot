import os.path
import datetime 
import random
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

import discord
from discord.ext import commands
from discord.utils import get

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

###########################
######### GLOBALS #########
###########################
gSheet          = None
gVRdancing      = None
gLogger         = None
gCtx            = None # Current discord invocation context

def SET_CTX(ctx):
    global gCtx
    gCtx = ctx

###########################
######## SETTINGS #########
###########################
class Settings:
    def __init__(self):
        self.lockXP         = True   # Whether mods can use all the XP gain commands
        self.maxXPGain      = 40     # max XP which can be added via addBootyXP command
        self.minLenUsername = 3      # min length of username
        self.maxLenUsername = 30     # max length of username
        self.newUserDM      = True   # Send out new user DM

    def XPLocked(self, user):
        return self.lockXP and not user.guild_permissions.administrator

gSettings = Settings()

###########################

BOT_DESCRIPTION = "A wholesome bot for our VRDancing Discord Server!"
CMD_PREFIX      = '$'
GSHEET_FOLDER   = 'GSheet/'
LOG_LEVEL       = logging.INFO
GSHEET_LINK     = "https://docs.google.com/spreadsheets/d/1QFHim9haIidy8sFablM4dBqUtYFuMiRtOTkBxAwDik0/edit#gid=0"
SPLIT_CHAR      = ';'  # Split character for giving sweatsession xp to users e.g. "NAME1;NAME2;NAME3"

ROLE_ADMIN      = 'Admin'
ROLE_MODERATOR  = 'Moderator'
ROLE_FITNESS_INSTRUCTOR = 'Fitness Instructor'

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

class Rank:
    def __init__(self, name, requiredPoints, color):
        self.name = name
        self.requiredPoints = requiredPoints
        self.color = color

# Define all ranks
gRanks = [
    Rank(RANK_FITNESS_NEWCOMER,  0,    0xffffff),
    Rank(RANK_FITNESS_CADET,     10,   0x607d8b),
    Rank(RANK_FITNESS_ROOKIE,    40,   0x1f8b4c),
    Rank(RANK_FITNESS_MAJOR,     80,   0x2ecc71),
    Rank(RANK_FITNESS_OFFICER,   150,  0x206694),
    Rank(RANK_FITNESS_GENERAL,   250,  0x3498db),
    Rank(RANK_FITNESS_CAPTAIN,   350,  0x71368a),
    Rank(RANK_FITNESS_COMMANDER, 500,  0x9b59b6),
    Rank(RANK_FITNESS_ADMIRAL,   650,  0xa84300),
    Rank(RANK_FITNESS_COMMODORE, 800,  0xe67e22),
    Rank(RANK_FITNESS_MARSHALL,  1000, 0xf1c40f)
]

def RankIndex(rank: str):
    for i in range(len(gRanks)):
        if gRanks[i].name == rank:
            return i

XP_SWEATSESSION = 10
XP_INSTRUCTOR   = 10
XP_BASIC_VIDEO  = 20
XP_YT_VIDEO     = 40

RANK_UP_CHANNEL_ID      = 827617550325907456
RANKS_CHANNEL_ID        = 827645739366481930
INTRODUCTION_CHANNEL_ID = 830858802277777438
RULES_CHANNEL_ID        = 830858785181925396
SELF_ROLES_CHANNEL_ID   = 830858814403379200
SWEATSESSION_CHANNEL_ID = 830885430492135424

###############################
def OnFitnessCadet():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_CADET}. Keep hitting it on the dancefloor!")
def OnFitnessRookie():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_ROOKIE}. Keep hitting it on the dancefloor!")
def OnFitnessMajor():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_MAJOR}. Keep hitting it on the dancefloor!")
def OnFitnessOfficer():
    return CYAN(f"Congratulations to your new rank! You are now a {RANK_FITNESS_OFFICER}. Keep hitting it on the dancefloor!")
def OnFitnessGeneral():
    return ORANGE(f"Congratulations to your new rank! You are now a {RANK_FITNESS_GENERAL}. Keep hitting it on the dancefloor!")
def OnFitnessCaptain():
    return ORANGE(f"Congratulations to your new rank! You are now a {RANK_FITNESS_CAPTAIN}. Keep hitting it on the dancefloor!")
def OnFitnessCommander():
    return ORANGE(f"Congratulations to your new rank! You are now a {RANK_FITNESS_COMMANDER}. Keep hitting it on the dancefloor!")
def OnFitnessAdmiral():
    return ORANGE(f"Congratulations to your new rank! You are now a {RANK_FITNESS_ADMIRAL}. Keep hitting it on the dancefloor!")
def OnFitnessCommodore():
    return ORANGE(f"Congratulations to your new rank! You are now a {RANK_FITNESS_COMMODORE}. Keep hitting it on the dancefloor!")
def OnFitnessMarshall():
    return ORANGE(f"Damn, you did it!!! You are now a {RANK_FITNESS_MARSHALL}. The Fitness Marshall is so proud of you!")

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
}

# Messages are part of an embed and posted in the ranks-up channel
def OnFitnessCadetChannel():
    return f"The journey just started..."
def OnFitnessRookieChannel():
    return f"Hey! You're getting into shape!"
def OnFitnessMajorChannel():
    return f"Well done! Shake that booty!!!"
def OnFitnessOfficerChannel():
    return f"Keep hitting it!"
def OnFitnessGeneralChannel():
    return f"Twerk that booty!"
def OnFitnessCaptainChannel():
    return f"Damn booty!!\nLookin' gooooood!"
def OnFitnessCommanderChannel():
    return f"Be careful that you're not\nfalling for the Marshall..."
def OnFitnessAdmiralChannel():
    return f"You really did fall for the Marshall, didn't you?"
def OnFitnessCommodoreChannel():
    return f"Holy Shit! That's amazing!\n Your booty is made out of stone!"
def OnFitnessMarshallChannel():
    return f"Damn, you did it!!!\nNever stop dancing!"

RankUpChannelMsg = {
           RANK_FITNESS_CADET     : OnFitnessCadetChannel,
           RANK_FITNESS_ROOKIE    : OnFitnessRookieChannel,
           RANK_FITNESS_MAJOR     : OnFitnessMajorChannel,
           RANK_FITNESS_OFFICER   : OnFitnessOfficerChannel,
           RANK_FITNESS_GENERAL   : OnFitnessGeneralChannel,
           RANK_FITNESS_CAPTAIN   : OnFitnessCaptainChannel,
           RANK_FITNESS_COMMANDER : OnFitnessCommanderChannel,
           RANK_FITNESS_ADMIRAL   : OnFitnessAdmiralChannel,
           RANK_FITNESS_COMMODORE : OnFitnessCommodoreChannel,
           RANK_FITNESS_MARSHALL  : OnFitnessMarshallChannel,
}

###########################
###########################
###########################
async def OnAddedToServer(member):
    # Post message in systems channel
    embed=discord.Embed(color=0x009dff)
    embed.set_thumbnail(url=f"{member.avatar_url}")
    embed.add_field(name=f"{member.name}", value=f"You are Booty No. #{len(gVRdancing.guild.members)}", inline=True)
    await gVRdancing.guild.system_channel.send(f"{member.mention} has joined the booty army!", embed=embed)
    #await message.add_reaction(":fm:")

    # Add roles to new user
    await gVRdancing.AddRole(member, RANK_FITNESS_NEWCOMER)

    # Send out private DM to user
    if (not gSettings.newUserDM):
        return

    introductionChannel = gVRdancing.GetChannel(INTRODUCTION_CHANNEL_ID)
    rulesChannel = gVRdancing.GetChannel(RULES_CHANNEL_ID)
    selfRoles = gVRdancing.GetChannel(SELF_ROLES_CHANNEL_ID)
    dm = f"""Hey {member.mention}! You finally made it! Welcome to our VRDancing Discord Server.
Please read the {introductionChannel.mention} for more information about our server.
Also read and react to the {rulesChannel.mention} to get full access.
Free free to give you some {selfRoles.mention}, so people know a bit about you!

Additionally, how about introducing yourself by setting a custom description?
If you reply to me with '{CMD_PREFIX}setdesc "INTRODUCE YOURSELF"' other people can query it with the {CMD_PREFIX}whois command.
Use double quotes and Shift+Enter for newlines!
Have fun and welcome again to the booty club!
    """
    await member.send(dm)

async def OnAddedToDatabase(member):    
    ranksChannel = gVRdancing.GetChannel(RANKS_CHANNEL_ID)
    sweatsessionChannel = gVRdancing.GetChannel(SWEATSESSION_CHANNEL_ID)
    dm  = f"""
Hi Active Booty!
You have just been added to the official VRDancing database.
From now on you can get booty experience by joining our {sweatsessionChannel.mention} or creating some cool dance videos!
For more information please check the {ranksChannel.mention} channel in our Discord Server.

Your username in the database has been set to your discord username ({member.mention}#{member.discriminator}).
Please change it to your vrchat username with '{CMD_PREFIX}setmyname'. You can check your username with '{CMD_PREFIX}myname'!"""

    embed = discord.Embed()
    embed.description = f"[Database]({GSHEET_LINK})"
    await member.send(dm, embed=embed)

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
        self.logger.warn(msg)

#################################################################       
##################### DISCORD USER ##############################
#################################################################
class DiscordUser():
    def __init__(self, dcUser, row, id, discordID, username, bootyXP, rank, dateJoined, userDesc):
        self.discordUser = dcUser # Can be None if this class was created as read-only (e.g. for top member query)
        self.row         = int(row)
        self.id          = int(id)
        self.discordID   = int(discordID)
        self.username    = username
        self.bootyXP     = int(bootyXP)
        self.rank        = rank
        self.dateJoined  = dateJoined
        self.userDesc    = userDesc

    async def SetXP(self, val):
        prev = self.bootyXP
        self.bootyXP = val        
        gSheet.DBSetBootyXP(self, self.bootyXP)
        await self.__CheckRank()
        return prev

    def SetUsername(self, name: str):
        prev = self.username
        self.username = name
        gSheet.DBSetUsername(self, self.username)
        return prev

    def SetDescription(self, desc: str):
        self.userDesc = desc
        gSheet.DBSetDescription(self, self.userDesc)

    def GetNextRankName(self):
        return self.__NextRank().name

    def GetNextRankMissingXP(self):
        nextRank = self.__NextRank()
        return nextRank.requiredPoints - self.bootyXP

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
        await gVRdancing.RemoveRole(self.discordUser, oldRank)
        self.rank = newRank
        await gVRdancing.AddRole(self.discordUser, self.rank)        

        newRankIndex = RankIndex(newRank)
        if newRankIndex < RankIndex(oldRank):
            return # Skip in case the new rank is lower (e.g. when admin changed the points manually)        

        try:
            # Send DM to user that his rank has changed
            await self.discordUser.send(RankUpDM[newRank]())

            # Send a message into the ranks channel and mention the user!
            embed=discord.Embed(color=gRanks[newRankIndex].color)
            #embed.set_thumbnail(url="https://yt3.ggpht.com/ytc/AAUvwnhb-qXCQ1EzAhubjtxaJhIwhzgtc0yQTFXPpv2n=s88-c-k-c0x00ffffff-no-rj")
            embed.set_thumbnail(url=self.discordUser.avatar_url)
            embed.add_field(name=f"{newRank}", value=RankUpChannelMsg[newRank](), inline=False)

            channel = gVRdancing.GetChannel(RANK_UP_CHANNEL_ID)
            await channel.send(f"{self.discordUser.mention} just achieved a new rank: {self.rank} with {self.bootyXP} XP ({gRanks[newRankIndex].requiredPoints} Needed)", embed=embed)
        except:
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
        async def on_member_join(member):
            await OnAddedToServer(member)               

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
                SET_CTX(ctx)
                admin = get(ctx.guild.roles, name=ROLE_ADMIN)
                return admin in ctx.author.roles or ctx.author.guild_permissions.administrator

            @commands.command(pass_context=True)
            async def DBSetBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """Sets booty experience for users"""
                SET_CTX(ctx)
                gLogger.Log(f"{ctx.author.name} changed booty points to {value} for {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = ""
                for user in members:
                    member = await gSheet.GetMember(user)
                    prev = await member.SetXP(value)
                    msg += f"Changed Booty XP for {user.mention}. New XP: {value} (Prev: {prev})\n"   
                await ctx.send(msg)   

            @commands.command(pass_context=True)
            async def DBSubbootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """Adds booty experience to an arbitrary amount of users"""
                SET_CTX(ctx)
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
                """Deletes users from the DB"""
                SET_CTX(ctx)
                for user in members:
                    success = gSheet.DBDeleteMember(user)
                    if success:
                        await ctx.send(f"Deleted {user.mention} successfully from DB")
                    else:
                        await ctx.send(f"Could not delete {user.mention} from DB (User doesn't exist)")
       
            @commands.command(pass_context=True)
            async def LockXP(self, ctx):
                """Locks the ability to change XP for Mods"""
                SET_CTX(ctx)
                gSettings.lockXP = True
                await ctx.send("```XP Gain locked for Mods```")

            @commands.command(pass_context=True)
            async def UnlockXP(self, ctx):
                """Unlocks the ability to change XP for Mods"""
                SET_CTX(ctx)
                gSettings.lockXP = False
                await ctx.send("```XP Gain unlocked for Mods```")

            @commands.command(pass_context=True)
            async def fitnessinstructor(self, ctx, newInstructor: discord.Member):
                """Sets a new fitness instructor for the upcoming week"""
                role = get(ctx.guild.roles, name=ROLE_FITNESS_INSTRUCTOR)
                for user in ctx.guild.members:
                    if role in user.roles:
                        await user.remove_roles(role)

                # Add new role to the new instructor
                await gVRdancing.AddRole(newInstructor, ROLE_FITNESS_INSTRUCTOR)
                channel = gVRdancing.GetChannel(SWEATSESSION_CHANNEL_ID)
                await ctx.send(f"Updated {ROLE_FITNESS_INSTRUCTOR} roles. {newInstructor.mention} You can now post in {channel.mention}. You've also gained {XP_INSTRUCTOR} Booty XP!")

                # Give additional XP for being an instructor
                member = await gSheet.GetMember(newInstructor)
                await member.SetXP(member.bootyXP + XP_INSTRUCTOR)

            
            @commands.command(pass_context=True)
            async def DM(self, ctx, members: commands.Greedy[discord.Member], dm: str):
                """Send a DM from the bot to one or multiples user"""
                for user in members:
                    await user.send(dm)

            @commands.command(pass_context=True)
            async def DMAll(self, ctx, roles: commands.Greedy[discord.Role], dm: str):
                """Sends a DM to all members in the server. BE VERY CAREFUL ABOUT THIS."""
                for user in ctx.guild.members:
                    if user.bot:
                        continue # Skip sending message to bots

                    if roles and not all(role in user.roles for role in roles):
                        continue # User don't have all roles
                    
                    await user.send(dm)

                    if not roles:
                        continue # DM sending to everyone without further notice

                    # Let user know which roles got the message
                    roleString = ""
                    for role in roles[0:-1]:
                        roleString += role.name + "|"  
                    roleString += roles[-1].name   
                    await user.send(CYAN(f"This message has been sent to all people with following roles: [{roleString}]"))

            @commands.command(pass_context=True)
            async def AddRoles(self, ctx, members: commands.Greedy[discord.Member], roles: commands.Greedy[discord.Role]):
                """Adds roles to an arbitrary amount of users"""
                for user in members:
                    for role in roles:
                        await user.add_roles(role)
                await ctx.reply(RED("Roles added"))


            @commands.command(pass_context=True)
            async def RemoveRoles(self, ctx, members: commands.Greedy[discord.Member], roles: commands.Greedy[discord.Role]):
                """Removes roles to an arbitrary amount of users"""
                for user in members:
                    for role in roles:
                        await user.remove_roles(role)
                await ctx.send(RED("Roles removed"))

        ####################### MOD COMMANDS ############################
        class Moderator(commands.Cog):
            """All commands usable by moderators"""

            async def cog_check(self, ctx):
                mod = get(ctx.guild.roles, name=ROLE_MODERATOR)
                return mod in ctx.author.roles

            @commands.command(pass_context=True)
            async def GiveBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
                """@Users VALUE"""
                SET_CTX(ctx)
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
                SET_CTX(ctx)
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
                    await member.SetXP(member.bootyXP + XP_SWEATSESSION)

                msg = f"Added {XP_SWEATSESSION} XP to {foundUsers}."
                if not missingUsers:
                    await ctx.send(msg)
                else:
                    foundUserMsg = msg+'\n' if foundUsers else ""
                    await ctx.send(f"{foundUserMsg}Couldn't find these members: {missingUsers} (Wrong name or they left the guild)")


            @commands.command(pass_context=True)
            async def GiveSweatsessionXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience to an arbitrary amount of users which attended a sweatsession"""
                SET_CTX(ctx)
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return
                gLogger.Log(f"{ctx.author.name} added sweatsession xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, XP_SWEATSESSION)
                await ctx.send(msg)

            @commands.command(pass_context=True)
            async def GiveVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience to someone who created a basic dance video"""
                SET_CTX(ctx)
                if (gSettings.XPLocked(ctx.author)):
                    await ctx.reply(XP_LOCK_MSG, mention_author = True)
                    return
                gLogger.Log(f"{ctx.author.name} added basic video xp to {DiscordUser.GetNamesOfMembersAsList(members)}")
                msg = await self.__AddBootyXP(members, XP_BASIC_VIDEO)
                await ctx.send(msg)

            @commands.command(pass_context=True)
            async def GiveYoutubeVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
                """Adds booty experience to someone who created a YouTube video for VRDancing"""
                SET_CTX(ctx)
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
                
            @commands.command(pass_context=True)
            async def Rank(self, ctx, members: commands.Greedy[discord.Member]):
                """Displays detailed information about a users rank"""
                SET_CTX(ctx)
                # Display your own rank if no user was listed
                if not members:
                    member = await gSheet.GetMember(ctx.author)
                    msg = f'```You have {member.bootyXP} booty points. Your rank is {member.rank}. You need {member.GetNextRankMissingXP()} more to reach the next rank of {member.GetNextRankName()}!```'
                    await ctx.reply(msg, mention_author=True)

                # Display rank of all users
                for user in members:
                    member = await gSheet.GetMember(user)
                    msg = f'```{member.username} has {member.bootyXP} booty points (Rank: {member.rank})!```'
                    await ctx.send(msg)

            @commands.command(pass_context=True)
            async def Chatmans(self, ctx):
                """EASTER EGG"""
                await ctx.reply('https://imgur.com/a/CMmabf6', mention_author=True)

            @commands.command(pass_context=True)
            async def Ranks(self, ctx):
                """Links the #rank channel"""
                channel = gVRdancing.GetChannel(RANKS_CHANNEL_ID)
                await ctx.send(f"Checkout the {channel.mention} channel for more information.")

            @commands.command(pass_context=True)
            async def SetMyName(self, ctx, name: str):
                """Changes your personal username in the database"""
                SET_CTX(ctx)
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
                await ctx.reply(f"Username was sucessfully updated to '{name}''.", mention_author=True)

            @commands.command(pass_context=True)
            async def MyName(self, ctx):
                """Get some information about yourself"""
                member = await gSheet.GetMember(ctx.author)
                await ctx.reply(f"Hi! Your username in the database is currently set to '{member.username}'", mention_author=True)

            @commands.command(pass_context=True)
            async def Highscores(self, ctx):
                """Display's a Highscore list for the top 10 members"""
                SET_CTX(ctx)              
                highscoreList = gSheet.GetTopMembers(10)

                longestName = 1
                for member in highscoreList:
                    longestName = max(longestName, len(member.username))

                msg = "```"
                for i in  range(len(highscoreList)):
                    member = highscoreList[i]
                    adjustedName = member.username.ljust(longestName)
                    msg += f"{i+1}: {adjustedName} with {member.bootyXP:4} booty XP. ({member.rank})\n" 
                
                embed = discord.Embed()
                embed.description = f"Goto [Database]({GSHEET_LINK}) to see the whole list."
                await ctx.send(f"{msg}```", embed = embed)

            @commands.command(pass_context=True)
            async def SetDesc(self, ctx, desc: str):
                """Introduce yourself by setting a custom description which you can query with the 'whois' command! The limit is 2000 characters."""
                SET_CTX(ctx)
                member = await gSheet.GetMember(ctx.author)
                member.SetDescription(desc)
                await ctx.reply(f"```Description sucessfully changed. You can check by using the '{CMD_PREFIX}whois' command without any arguments!```", mention_author=True)

            @commands.command(pass_context=True)
            async def WhoIs(self, ctx, user: discord.Member = None):
                """Returns a custom set message from a any user. Change it with the 'setdesc' command!"""
                SET_CTX(ctx)
                if (user is None):
                    user = ctx.author
                    member = await gSheet.GetMember(user)
                    await ctx.reply(f"Your custom description:\n```{member.userDesc}```", mention_author=True)
                else:
                    member = await gSheet.GetMember(user)
                    await ctx.reply(f"```{member.username}:\n{member.userDesc}```", mention_author=True)

            @WhoIs.error
            async def whois_error(self, ctx, error):
                await ctx.send(f"```Member hasn't been added to the database yet...```")

            @commands.command(pass_context=True)
            async def FM(self, ctx):
                """EASTER EGG"""
                await ctx.send('https://cdn.discordapp.com/attachments/793977209642811393/831637815488938014/thing1.gif')

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
    async def RemoveRole(self, user: discord.Member, roleName: str):
        role = get(self.guild.roles, name=roleName)
        await user.remove_roles(role)

    async def AddRole(self, user: discord.Member, roleName: str):
        role = get(self.guild.roles, name=roleName)
        await user.add_roles(role)

    def GetChannel(self, id):
        return self.guild.get_channel(id)

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
        row[self.dbIndexBootyXP].value    = '0'
        row[self.dbIndexRank].value       = RANK_FITNESS_NEWCOMER
        row[self.dbIndexDateJoined].value = datetime.datetime.now().strftime("%d.%m.%Y")
        row[self.dbIndexUserDesc].value   = f"Your awesome custom description. (Change it with '{CMD_PREFIX}setdesc')"

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

        highscoreList = gSheet.GetTopMembers(10)

        testUser = discord.User
        #testUser.id = 236510124070404097
        testUser.id = 42
        testUser.name = 'Test'
        member = self.GetMember(testUser)
        #member.SetXP(600)
        self.DBDeleteMember(testUser)

        testUser.id = 26516126
        #testUser.name = 'Scolly'
        self.DBCreateNewMember(testUser)
        self.DBDeleteMember(testUser)

        #member = self.GetMember(testUser)
        #prev = member.SetXP(42)
        #prev = member.SetXP(prev)


        #result_col = sheet.col_values(1) #See individual column
        #result_cell = sheet.cell(1, 1) # See particular cell

        #sheet.update_cell(2,1,'42')  #Change value
        #sheet.update_cell(2,1,'0')  #Change value

        print('Test done')


#################################################################       
############################ MAIN ###############################
#################################################################
def main():
    global gSheet
    global gLogger

    gLogger = Logger('vrdancing', LOG_LEVEL)

    gSheet = GoogleSpreadSheet('VRDancing',  GSHEET_FOLDER + 'vrdancing_keys.json')
    #gSheet.Test('Database')

    VRDancing()

if __name__ == "__main__":
    main()














    
