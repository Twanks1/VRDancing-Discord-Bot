import discord
async def OnAddedToDatabase(user: discord.user):    
    ranksChannel = gVRdancing.GetChannel(gSettings.ChannelIDRanks())
    sweatsessionChannel = gVRdancing.GetChannel(gSettings.ChannelIDSweatSession())
    dm  = f"""
Hi Active Booty!
You have just been added to the official VRDancing database.
From now on you can get booty experience by joining our {sweatsessionChannel.mention} or creating some cool dance videos!
For more information please check the {ranksChannel.mention} channel in our Discord Server.

Your username in the database has been set to your discord username ({user.mention}#{user.discriminator}).
Please change it to your vrchat username with '{CMD_PREFIX}setmyname "MY FANCY NAME"'. You can check your username with '{CMD_PREFIX}myname'!"""

    #embed = discord.Embed()
    ##embed.description = f"[Database]({GSHEET_LINK})"
    await user.send(dm)