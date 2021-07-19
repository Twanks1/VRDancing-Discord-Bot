import config
import sentry_sdk
import discord
from discord.ext import commands

import asyncpg as db

from vrdancing.cogs.eastereggs import *
from vrdancing.cogs.dmall import *
from vrdancing.cogs.modcommands import *
from vrdancing.events.on_member_join import *
from vrdancing.events.on_command_error import *
from vrdancing.cogs.basecommands import *
from vrdancing.cogs.admincommands import *
class VRDancing(discord.Client):
    

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        
        bot = commands.Bot(
            command_prefix=config.PREFIX, intents=intents, case_insensitive=True
        )
        self.bot = bot

        if not config.SENTRY_DSN == "":
            sentry_sdk.init(
                config.SENTRY_DSN,
                traces_sample_rate=1.0
            )
            config.Glogger.Log("Sentry initialized")
            
        def GetChannel(self, id):
            return self.guild.get_channel(id)
        @bot.event
        async def on_ready():
            config.Glogger.Log("Logged in as {0.user}".format(bot))
            config.db = await db.create_pool(**config.DATABASE_INFORMATION)
            # Go ahead and restart the bot try now

        #bot.add_cog(dmall())
        bot.add_cog(on_command_error())
        bot.add_cog(adminCommands())
        bot.add_cog(basecommands())
        bot.add_cog(modCommands())
        bot.add_cog(on_member_join())
        bot.add_cog(eastereggs())
        bot.run(config.TOKEN)

    

if __name__ == "__main__":
    VRDancing()
