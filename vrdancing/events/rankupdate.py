from config import *
from vrdancing.utils.colors import *
from vrdancing.database.storage import *
from vrdancing.utils.check_rank import RankIndex
from vrdancing.cards.genrankcard import GenerateRankCard


async def AddSWSXP(usr: str, ctx):
    row = await GetDBUser(usr)
    await config.db.execute(
        "UPDATE ranks SET bootyxp = $1 WHERE discordid = $2",
        row["bootyxp"]+10,
        row["discordid"]
    )
    await config.db.execute(
        "UPDATE ranks SET swsxp = $1 WHERE discordid = $2",
        True,
        row["discordid"]
    )
    await UpdateRank(usr, ctx)
    
async def GetXP(usr: str):
    row = await config.db.fetchrow("""
        select result.position, result.username, bootyxp
        from (
            select *,
            row_number() over(
               order by bootyxp desc
            ) as position
        from ranks
        ) result
        where username = $1;
    """, usr)
    return row['position']


async def UpdateRank(usr: str, ctx):
    row = await GetDBUser(usr)
    currank = row['rank']
    for rank in config.gRanks:
        if row['bootyxp'] < rank.requiredPoints:
            break
        currank = rank
    if row['rank'] != currank.name:
        await onRankChange(ctx, row['username'], currank.name)

async def onRankChange(ctx, usr: str, rank: str):
    row = await GetDBUser(usr)
    oldRank = row['rank']
    user = ctx.guild.get_member(int(row["discordid"]))
    #await RemoveRole(ctx, user, row['rank'])
    try: 
        await RemoveRole(ctx, user, row['rank'])
    except:
        config.Glogger.Warn(f"Couldn't remove role {row['rank']} from user {usr} (Does the role exist?)")

    await SetRank(usr, rank)

    
    try:
        await AddRole(ctx, user, rank)        
    except:
        config.Glogger.Warn(f"Couldn't add role {row['rank']} to user {usr} (Does the role exist?)")

    newRank = rank
    newRankIndex = RankIndex(newRank)
    if newRankIndex < RankIndex(oldRank):
        return
    
    try:
        await user.send(RankUpDM[newRank]())

        # Send the rank card to the user as DM
        card = await GenerateRankCard(user)
        await user.send(file=card)

        channel = ctx.guild.get_channel(config.RANK_UP)            
        card = await GenerateRankCard(user)
        await channel.send(f"{user.mention} just achieved a new rank: {rank} ({config.gRanks[newRankIndex].requiredPoints} XP was needed)", file=card)
    except:
        config.Glogger.Warn("Failed to send a rank up message in the rank up channel (Wrong channel id set?)")
        pass



def OnFitnessCadet():
    return CYAN(
        f"Congratulations to your new rank! You are now a {RANK_FITNESS_CADET}. The journey just started..."
    )
def OnFitnessRookie():
    return CYAN(f"You're getting into shape! You are now a {RANK_FITNESS_ROOKIE}.")
def OnFitnessMajor():
    return CYAN(f"Well done! Shake that booty!!! You are now a {RANK_FITNESS_MAJOR}.")
def OnFitnessOfficer():
    return CYAN(
        f"Congratulations to your new rank! You are now a {RANK_FITNESS_OFFICER}. Keep hitting it on the dancefloor!"
    )
def OnFitnessGeneral():
    return ORANGE(f"Twerk that booty! You are now a {RANK_FITNESS_GENERAL}.")
def OnFitnessCaptain():
    return ORANGE(
        f"Damn booty!! Lookin' gooooood! You are now a {RANK_FITNESS_CAPTAIN}."
    )
def OnFitnessCommander():
    return ORANGE(
        f"You are now a {RANK_FITNESS_COMMANDER}. Be careful that you're not falling for the Marshall.."
    )
def OnFitnessAdmiral():
    return ORANGE(
        f"Congratzz! You are now a {RANK_FITNESS_ADMIRAL}. You really did fall for the Marshall, didn't you?"
    )
def OnFitnessCommodore():
    return ORANGE(
        f"Holy Shit! That's amazing! Your booty is made out of stone! You are now a {RANK_FITNESS_COMMODORE}."
    )
def OnFitnessMarshall():
    return ORANGE(
        f"Damn, you did it!!! You are now a {RANK_FITNESS_MARSHALL}. The Fitness Marshall is so proud of you!"
    )
def OnFitnessMarshall2():
    return ORANGE(f"Holy fucking moly... You are now a {RANK_FITNESS_MARSHALL2}.")
def OnFitnessMarshall3():
    return ORANGE(f"What the fucking hell? You are now a {RANK_FITNESS_MARSHALL3}.")
def OnFitnessGod():
    return ORANGE(
        f"You are literally a god amongst humans. You are now a {RANK_FITNESS_GOD}."
    )
RankUpDM = {
    RANK_FITNESS_CADET: OnFitnessCadet,
    RANK_FITNESS_ROOKIE: OnFitnessRookie,
    RANK_FITNESS_MAJOR: OnFitnessMajor,
    RANK_FITNESS_OFFICER: OnFitnessOfficer,
    RANK_FITNESS_GENERAL: OnFitnessGeneral,
    RANK_FITNESS_CAPTAIN: OnFitnessCaptain,
    RANK_FITNESS_COMMANDER: OnFitnessCommander,
    RANK_FITNESS_ADMIRAL: OnFitnessAdmiral,
    RANK_FITNESS_COMMODORE: OnFitnessCommodore,
    RANK_FITNESS_MARSHALL: OnFitnessMarshall,
    RANK_FITNESS_MARSHALL2: OnFitnessMarshall2,
    RANK_FITNESS_MARSHALL3: OnFitnessMarshall3,
    RANK_FITNESS_GOD: OnFitnessGod,
}
