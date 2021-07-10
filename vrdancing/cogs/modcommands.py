import discord
import config 
from discord.ext import commands 
from vrdancing.database.storage import *
from vrdancing.events.rankupdate import AddSWSXP
class modCommands(commands.Cog):
    def __init__(self) -> None:
        return

    async def ORANGE(str):
        return "```fix\n" + str + "```"

    async def cog_check(self, ctx):
        admin = discord.utils.get(ctx.guild.roles, name = config.ROLE_MODERATOR)
        mod = discord.utils.get(ctx.guild.roles, name = config.ROLE_ADMIN)
        return mod in ctx.author.roles or admin in ctx.author.roles

    @commands.command(pass_context = True)
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
            if member['swsxp']:
                continue
            await ctx.send(f"Adding {config.XP_SWEATSESSION} booty xp to {member['username']}...")
            await AddSWSXP(user, ctx)
            dm = (f"Gained {config.XP_SWEATSESSION} booty xp for joining our weekly sweat session! (New XP: {member['bootyxp']+10})\nUse {config.PREFIX}rank to see your current rank.")
            await ctx.guild.get_member(int(member['discordid'])).send(dm)
        config.Glogger.Log(f"{ctx.author.name} added {config.XP_SWEATSESSION} booty xp to {foundUsers}")
        msg = f"Added {config.XP_SWEATSESSION} XP to {foundUsers}."
        if not missingUsers:
            await ctx.send(msg)
        else:
            foundUserMsg = msg+'\n' if foundUsers else ""
            await ctx.send(f"{foundUserMsg}Couldn't find these members: {missingUsers} (Wrong name or they left the guild)")

    @commands.command(pass_context = True)
    async def ResetSWSxp(self,ctx):
        await resetSWS()
        await ctx.send("Reset SWS XP variable.")

    @commands.command(pass_context = True)
    async def SSXPSetName(self, ctx,strUser:str , user: discord.Member):
        if(config.LOCKXP):
            await ctx.reply(config.XP_LOCK_MSG, mention_author = True)
            return
        member = await GetorCreateDBUser(strUser, user)
        await config.db.execute(
            "UPDATE ranks SET username = $1 WHERE discordid = $2",
            strUser,
            str(user.id)
        )
        await AddSWSXP(strUser, ctx)
        row = await GetDBUser(strUser)
        await ctx.send(f"Adding {config.XP_SWEATSESSION} booty xp to {user.mention}... (New XP: {row['bootyxp']})")
        dm = (f"Gained {config.XP_SWEATSESSION} booty xp for joining our weekly sweat session! (New XP: {row['bootyxp']})\nUse {config.PREFIX}rank to see your current rank.")
        await user.send(dm)
