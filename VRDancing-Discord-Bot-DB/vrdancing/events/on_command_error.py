import discord
from discord.ext import commands
class on_command_error(commands.Cog):
    def __init__(self) -> None:
        return

    @commands.Cog.listener()
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
