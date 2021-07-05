import config
import discord
from vrdancing.utils.discord.role_utils import AddRole
from vrdancing.utils.discord.channel_utils import GetChannel


async def OnFitnessInstructor(user: discord.user):

    sweatsessionChannel = GetChannel(config.SWEATSESSION)
    sweatsessionPrepChannel = GetChannel(config.SWEATSESSION_PREP)

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
    await AddRole(user, config.ROLE_FITNESS_INSTRUCTOR)

    # Give additional XP for being an instructor
    ##member = await gSheet.GetMember(user)
    ##await member.SetXP(member.bootyXP + XP_INSTRUCTOR)
