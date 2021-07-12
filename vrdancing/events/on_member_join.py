import discord
import config

from discord.ext import commands
import VRDancing
from vrdancing.utils.discord.role_utils import AddRoles
from vrdancing.database.storage import DBCreateNewMember

class on_member_join(commands.Cog):
    def __init__(self) -> None:
        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # setup system Channel.

        await AddRoles(
            member,
            [
                config.RANK_FITNESS_NEWCOMER,
                config.ROLE_SPLIT_OTHER_ROLES,
                config.ROLE_SPLIT_SPECIAL_ROLES,
            ],
        )
        await GetorCreateDBUser(member.name, member)

        if not config.NEWUSERDM:
            return

        introductionChannel = member.guild.get_channel(config.INTRODUCTION)
        rulesChannel = member.guild.get_channel(config.RULES)
        ranksChannel = member.guild.get_channel(config.RANKS)
        selfRoles = member.guild.get_channel(config.SELF_ROLES)
        dm = f"""Hey {member.mention}! You finally made it! Welcome to our VRDancing Discord Server.
Please read the {introductionChannel.mention} for more information about our server.
Also read and react to the {rulesChannel.mention} to get full access.
Free free to give you some {selfRoles.mention}, so people know a bit about you!
Join our weekly dance session and gain some booty ranks! Checkout {ranksChannel.mention}!

Additionally, how about introducing yourself by setting a custom description?
Reply to me with "{config.PREFIX}whois" to see your own customized banner!
Use '{config.PREFIX}setdesc "INTRODUCE YOURSELF"' to change the text.
Put everything into double quotes and use Shift+Enter for newlines! (Max {config.MAXLENDESC} characters)
Have fun and welcome again to the booty club!
    """
        await member.send(dm)
