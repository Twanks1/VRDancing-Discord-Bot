import discord
import config

from discord.ext import commands
from discord.utils import get
class dmall(commands.Cog):
    def __init__(self) -> None:
        return
    
    async def cog_check(self, ctx):
        admin = get(ctx.guild.roles, name=config.ROLE_ADMIN)
        return admin in ctx.author.roles or ctx.author.guild_permissions.administrator

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