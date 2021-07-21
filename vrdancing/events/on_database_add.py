import discord
import config
async def OnAddedToDatabase(user: discord.user):    
    ranksChannel = user.guild.get_channel(config.RANKS)
    sweatsessionChannel = user.guild.get_channel(config.SWEATSESSION)
    dm  = f"""
Hi Active Booty!
You have just been added to the official VRDancing database.
From now on you can get booty experience by joining our {sweatsessionChannel.mention} or creating some cool dance videos!
For more information please check the {ranksChannel.mention} channel in our Discord Server.

Your username in the database has been set to your discord username ({user.mention}#{user.discriminator}).
Please change it to your vrchat username with '{config.PREFIX}setmyname "MY FANCY NAME"'. You can check your username with '{config.PREFIX}myname'!"""

    #embed = discord.Embed()
    ##embed.description = f"[Database]({GSHEET_LINK})"
    await user.send(dm)