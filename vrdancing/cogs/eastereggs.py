import discord

from discord.ext import commands
from vrdancing.database.storage import DBCreateNewMember
from vrdancing.database.storage import GetDBUser
from vrdancing.events.rankupdate import *

class eastereggs(commands.Cog):
    def __init__(self) -> None:
        return

    @commands.command(pass_context=True, hidden=True)
    async def Chatmans(self, ctx: discord.ext.commands.Context) -> None:
        await ctx.send("https://imgur.com/a/CMmabf6")

    @commands.command(pass_context=True, hidden=True)
    async def Kanami(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://imgur.com/a/yQX0GO0")

    @commands.command(pass_context=True, hidden=True)
    async def Cinte(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://imgur.com/a/hYdTbY6")

    @commands.command(pass_context=True, hidden=True)
    async def MiniGreen(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://imgur.com/a/TxluDit")

    @commands.command(pass_context=True, hidden=True)
    async def Raestar(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://media.giphy.com/media/IcCd2FhIzuIo0/giphy.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Haley(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://media.giphy.com/media/mDTC6m4Osb9p4ppOoX/giphy.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Allison(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://media.giphy.com/media/MF0p6EtTvgTYprwpPE/giphy.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Scolly(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://media.giphy.com/media/EQ1X2DtTRp1aE/giphy.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Pony(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://tenor.com/3Y7h.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Ride(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://tenor.com/3Y7D.gif")

    @commands.command(pass_context=True, hidden=True)
    async def Booty(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://tenor.com/bcoCU.gif")

    @commands.command(pass_context=True, hidden=True)
    async def FM(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send(
            "https://cdn.discordapp.com/attachments/793977209642811393/831637815488938014/thing1.gif"
        )
    @commands.command(pass_context=True, hidden=True)
    async def Evelyno(self, ctx: discord.ext.commands.Context) -> None:
        """EASTER EGG"""
        await ctx.send("https://media.discordapp.net/attachments/793977209642811393/864607188138852383/DabBattle.gif")