import discord
import config 
from discord.ext import commands 
from discord.utils import get 
import VRDancing
from vrdancing.database.storage import *
from vrdancing.events.rankupdate import AddSWSXP
from vrdancing.events.rankupdate import UpdateRank

class adminCommands(commands.Cog):
    def __init__(self) -> None:
        return

    async def cog_check(self, ctx):
        admin = get(ctx.guild.roles, name=config.ROLE_ADMIN)
        return admin in ctx.author.roles or ctx.author.guild_permissions.administrator

    @staticmethod
    def GetNamesOfMembersAsList(members):
        if not members:
            return ""
        names = "["+members[0].name
        for user in members[1:]:
            names += ", " + user.name
        return names + "]"


    @commands.command(pass_context=True)
    async def DBSetBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
        """Sets booty experience for users. Usage: cmd @userN value"""
        config.Glogger.Log(f"{ctx.author.name} changed booty points to {value} for {self.GetNamesOfMembersAsList(members)}")
        msg = ""
        for user in members:
            #member = await GetDBUserByID(str(user.id))
            member = await GetorCreateDBUser(str(user.id), user)
            prev = member['bootyxp']
            await config.db.execute(
                "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
                value,
                member["discordid"]
            )
            await UpdateRank(member["username"],ctx)
            msg += f"Changed Booty XP for {user.mention}. New XP: {value} (Prev: {prev})\n"   
        await ctx.send(msg)   

    @commands.command(pass_context=True)
    async def DBSubBootyXP(self, ctx, members: commands.Greedy[discord.Member], value: int):
        """Removes booty experience. Usage: cmd @userN value"""
        config.Glogger.Log(f"{ctx.author.name} subtracted {value} booty points for {self.GetNamesOfMembersAsList(members)}")
        msg = ""
        for user in members:
            member = await GetDBUserByID(str(user.id))
            newXP = max(0, member["bootyxp"] - value)
            await config.db.execute(
                "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
                newXP,
                member["discordid"]
            )
            await UpdateRank(member["username"],ctx)
            msg += f"Subtracted {value} booty points from {user.name}. New XP: {newXP}\n"
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def DBDeleteUser(self, ctx, members: commands.Greedy[discord.Member]):
        """Deletes users from the DB. Usage: cmd @userN"""
        config.Glogger.Log(f"{ctx.author.name} deletes users {self.GetNamesOfMembersAsList(members)} in db")
        for user in members:
            config.db.execute(
                "DELETE FROM ranks WHERE discordid = $1",
                str(user.id)
            )
            await ctx.send(f"Deleted {user.mention} successfully from DB")

    @commands.command(pass_context=True)
    async def FitnessInstructor(self, ctx, user: discord.Member):
        """Sets a new fitness instructor for the upcoming week"""

        # Remove fitness instructor role from previous instructors
        role = get(ctx.guild.roles, name=config.ROLE_FITNESS_INSTRUCTOR)
        for u in ctx.guild.members:
            if role in u.roles:
                await u.remove_roles(role)

        sweatsessionChannel = ctx.guild.get_channel(config.SWEATSESSION)
        sweatsessionPrepChannel = ctx.guild.get_channel(config.SWEATSESSION_PREP)

        dm = f"""Hey Booty!
        You have been selected to be the Fitness Instructor for our {sweatsessionChannel.mention}
        Your job is to create a playlist of songs for us. You are free to pick any song you like.
        You can even create own ones if you feel extremely dedicated! Be creative and give everyone a good time!
        The session should last about an hour long (~15 songs), but feel free to make it a little longer if you want.
        Please post the finished playlist at least a day before the session in {sweatsessionPrepChannel.mention}. 
        You can also drop any questions in there. The channel is for the instructor and mods/admins only.
    
        Last but not least write a custom message to everyone in {sweatsessionChannel.mention} and @Ping-Weekly Sweat Session.
        Feel free to do this whenever you want. The sooner the better though!
        The Fitness Marshall thanks you for your services. {config.XP_INSTRUCTOR} Booty XP earned!"""

        await user.send(dm)

        # Add role
        await AddRole(ctx, user, config.ROLE_FITNESS_INSTRUCTOR)
        member = await GetDBUserByID(str(user.id))
        newXP = int(member["bootyxp"]) + int(config.XP_INSTRUCTOR)
        await config.db.execute(
            "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
            newXP,
            str(user.id)
        )

        await ctx.send(f"Updated {config.ROLE_FITNESS_INSTRUCTOR} roles. New Instructor for this week is {user.mention}. You've also gained {config.XP_INSTRUCTOR} booty XP!")
                
        config.Glogger.Log(f"{ctx.author.name} set a new fitness instructor: {user.name}")