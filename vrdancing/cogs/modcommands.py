import discord
import time
import config
from discord.ext import commands
from vrdancing.database.storage import *
from vrdancing.events.rankupdate import AddSWSXP
from vrdancing.events.rankupdate import UpdateRank


class modCommands(commands.Cog):
    def __init__(self) -> None:
        return

    async def ORANGE(str):
        return "```fix\n" + str + "```"

    async def cog_check(self, ctx):
        admin = discord.utils.get(ctx.guild.roles, name=config.ROLE_MODERATOR)
        mod = discord.utils.get(ctx.guild.roles, name=config.ROLE_ADMIN)
        return mod in ctx.author.roles or admin in ctx.author.roles

    @staticmethod
    def GetNamesOfMembersAsList(members):
        if not members:
            return ""
        names = "[" + members[0].name
        for user in members[1:]:
            names += ", " + user.name
        return names + "]"

    @commands.command(pass_context=True)
    async def SSXP(self, ctx, str: str):
        missingUsers = []
        foundUsers = []

        users = str.split(config.SPLIT_CHAR)
        for user in users:
            member = await GetDBUser(user)
            if not member:
                missingUsers.append(user)
                continue
            foundUsers.append(user)
            if member["swsxp"]:
                continue
            await ctx.send(
                f"Adding {config.XP_SWEATSESSION} booty xp to {member['username']}..."
            )
            await AddSWSXP(user, ctx)
            dm = f"Gained {config.XP_SWEATSESSION} booty xp for joining our weekly sweat session! (New XP: {member['bootyxp']+10})\nUse {config.PREFIX}rank to see your current rank."
            await ctx.guild.get_member(int(member["discordid"])).send(dm)
            time.sleep(2)
        config.Glogger.Log(
            f"{ctx.author.name} added {config.XP_SWEATSESSION} booty xp to {foundUsers}"
        )
        msg = f"Added {config.XP_SWEATSESSION} XP to {foundUsers}."
        if not missingUsers:
            await ctx.send(msg)
        else:
            foundUserMsg = msg + "\n" if foundUsers else ""
            await ctx.send(
                f"{foundUserMsg}Couldn't find these members: {missingUsers} (Wrong name or they left the guild)"
            )

    @commands.command(pass_context=True)
    async def ResetSWSxp(self, ctx):
        await resetSWS()
        await ctx.send("Reset SWS XP variable.")

    @commands.command(pass_context=True)
    async def SSXPSetName(self, ctx, strUser: str, user: discord.Member):
        if config.LOCKXP:
            await ctx.reply(config.XP_LOCK_MSG, mention_author=True)
            return
        member = await GetorCreateDBUser(strUser, user)
        await config.db.execute(
            "UPDATE ranks SET username = $1 WHERE discordid = $2", strUser, str(user.id)
        )
        await AddSWSXP(strUser, ctx)
        row = await GetDBUser(strUser)
        await ctx.send(
            f"Adding {config.XP_SWEATSESSION} booty xp to {user.mention}... (New XP: {row['bootyxp']})"
        )
        dm = f"Gained {config.XP_SWEATSESSION} booty xp for joining our weekly sweat session! (New XP: {row['bootyxp']})\nUse {config.PREFIX}rank to see your current rank."
        await user.send(dm)

    @commands.command(pass_context=True)
    async def DBAddBootyXP(
        self, ctx, members: commands.Greedy[discord.Member], value: int
    ):
        """@Users VALUE"""
        # if (gSettings.XPLocked(ctx.author)):
        #   await ctx.reply(XP_LOCK_MSG, mention_author = True)
        #    return

        if value <= 0 or value > config.MAXXPGAIN:
            await ctx.reply(
                f"Value must lie within 1 - {config.MAXXPGAIN}!", mention_author=True
            )
            return
        config.Glogger.Log(
            f"{ctx.author.name} added {value} booty xp to {self.GetNamesOfMembersAsList(members)}"
        )
        msg = ""
        for user in members:
            member = await GetDBUserByID(str(user.id))
            newXP = member["bootyxp"] + value
            await config.db.execute(
                "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
                newXP,
                member["discordid"],
            )
            await UpdateRank(member["username"], ctx)
            msg += f"Added {value} booty points to {user.mention}. New XP: {newXP}\n"

        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def GiveVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
        """Adds booty experience worth of a basic dance video. Usage: cmd @user"""
        # if (gSettings.XPLocked(ctx.author)):
        #    await ctx.reply(XP_LOCK_MSG, mention_author = True)
        #    return
        config.Glogger.Log(
            f"{ctx.author.name} added basic video xp to {self.GetNamesOfMembersAsList(members)}"
        )
        msg = ""
        for user in members:
            member = await GetDBUserByID(str(user.id))
            newXP = member["bootyxp"] + config.XP_BASIC_VIDEO
            await config.db.execute(
                "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
                newXP,
                member["discordid"],
            )
            await UpdateRank(member["username"], ctx)
            msg += f"Added {config.XP_BASIC_VIDEO} booty points to {user.mention}. New XP: {newXP}\n"

        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def GiveYoutubeVideoXP(self, ctx, members: commands.Greedy[discord.Member]):
        """Adds booty experience worth of a YouTube video for VRDancing. Usage: cmd @user"""
        # if (gSettings.XPLocked(ctx.author)):
        #    await ctx.reply(XP_LOCK_MSG, mention_author = True)
        #    return
        config.Glogger.Log(
            f"{ctx.author.name} added YT video xp to {self.GetNamesOfMembersAsList(members)}"
        )
        msg = ""
        for user in members:
            member = await GetDBUserByID(str(user.id))
            newXP = member["bootyxp"] + config.XP_YT_VIDEO
            await config.db.execute(
                "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
                newXP,
                member["discordid"],
            )
            await UpdateRank(member["username"], ctx)
            msg += f"Added {config.XP_YT_VIDEO} booty points to {user.mention}. New XP: {newXP}\n"

        await ctx.send(msg)
