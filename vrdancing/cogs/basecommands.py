import discord
import config
from discord.ext import commands
from vrdancing.database.storage import *
from vrdancing.events.rankupdate import AddSWSXP
from vrdancing.cards.genrankcard import GenerateRankCard
from vrdancing.cards.gendesccard import GenerateDescCard


class basecommands(commands.Cog):
    def __init__(self) -> None:
        return

    @commands.command(pass_context=True)
    async def SetMyName(self, ctx, name: str):
        """Changes your personal username in the database"""
        config.Glogger.Log(f"{ctx.author.name} changed his name to {name}")
        if len(name) < config.MINLENUSERNAME:
            await ctx.reply(
                f"Username too short. Name must be between {config.MINLENUSERNAME} and {config.MAXLENUSERNAME} letters.",
                mention_author=True,
            )
            return
        if len(name) > config.MAXLENUSERNAME:
            await ctx.reply(
                f"Username too long. Name must be between {config.MINLENUSERNAME} and {config.MAXLENUSERNAME} letters.",
                mention_author=True,
            )
            return
        member = await GetDBUser(name)
        if member:
            await ctx.reply(
                f"Username already taken. Please chooser another one.",
                mention_author=True,
            )
            return
        await SetName(name, ctx.author)
        await ctx.reply(
            f"Username was changed to '{name}''. Please make sure this is your vrchat username (case sensitive!)",
            mention_author=True,
        )

    @commands.command(pass_context=True)
    async def Rank(self, ctx, members: commands.Greedy[discord.Member]):
        """Shows a rank. If no argument is provided it shows your rank."""
        # Display your own rank if no argument was provided
        if not members:
            if len(ctx.view.buffer) > len("$rank"):
                await ctx.reply(
                    "Invalid arguments provided. Either ping a member with @ or use no argument to show your rank.",
                    mention_author=True,
                )
                return
            card = await GenerateRankCard(ctx.author)
            await ctx.send(file=card)

        # Display rank of all given users
        for user in members:
            card = await GenerateRankCard(user)
            await ctx.send(file=card)

    @commands.command(pass_context=True)
    async def MyName(self, ctx):
        """Get some information about yourself"""
        member = await GetDBUserByID(str(ctx.author.id))
        await ctx.reply(
            f"Hi! Your username in the database is currently set to '{member['username']}'",
            mention_author=True,
        )

    @commands.command(pass_context=True)
    async def SetDesc(self, ctx, desc: str):
        """Introduce yourself by setting a custom description which you can query with the 'whois' command! Execute the command without args to see the limit."""
        if len(desc) < config.MINLENDESC:
            await ctx.reply(
                f"Description too short. Character amount must lie between {config.MINLENDESC} and {config.MAXLENDESC}! Also don't forget to put everything into ''!"
            )
            return
        if len(desc) > config.MAXLENDESC:
            await ctx.reply(
                f"Description too long. Character amount must lie between {config.MINLENDESC} and {config.MAXLENDESC}!"
            )
            return

        config.Glogger.Log(f"{ctx.author.name} updated there description")
        await SetDesc(desc, ctx.author)
        await ctx.reply(
            f"```Description sucessfully changed. You can check by using the '{config.PREFIX}whois' command without any arguments!```",
            mention_author=True,
        )

    @commands.command(pass_context=True)
    async def WhoIs(self, ctx, user: discord.Member = None):
        """Returns a custom set message from a any user. Change it with the 'setdesc' command!"""
        if user is None:
            user = ctx.author

        card = await GenerateDescCard(user)
        await ctx.send(file=card)

    @WhoIs.error
    async def whois_error(self, ctx, error):
        await ctx.send(f"```Member doesn't exist in the database...```")
