import discord
import config 
from discord.ext import commands 
from vrdancing.database.storage import GetDBUser
from vrdancing.events.rankupdate import AddSWSXP
class modCommands(commands.Cog):
    def __init__(self) -> None:
        return

    async def cog_check(self, ctx):
        admin = discord.utils.get(ctx.guild.roles, name = config.ROLE_MODERATOR)
        mod = discord.utils.get(ctx.guild.roles, name = config.ROLE_ADMIN)
        return mod in ctx.author.roles or admin in ctx.author.roles

    @commands.command(pass_context = True)
    async def SweatsessionXP(self, ctx, str: str):
        missingUsers = []
        foundUsers = []

        users = str.split(config.SPLIT_CHAR)
        for user in users: 
            member = await GetDBUser(user)
            if not member:
                missingUsers.append(user)
                continue
            foundUsers.append(user)
            await ctx.send(f"Adding {config.XP_SWEATSESSION} booty xp to {member['username']}...")
            await AddSWSXP(user, ctx)
        config.Glogger.Log(f"{ctx.author.name} added {config.XP_SWEATSESSION} booty xp to {foundUsers}")
        msg = f"Added {config.XP_SWEATSESSION} XP to {foundUsers}."
        if not missingUsers:
            await ctx.send(msg)
        else:
            foundUserMsg = msg+'\n' if foundUsers else ""
            await ctx.send(f"{foundUserMsg}Couldn't find these members: {missingUsers} (Wrong name or they left the guild)")