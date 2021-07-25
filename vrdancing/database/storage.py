import config
import discord
import datetime
from vrdancing.utils.discord.role_utils import RemoveRole, AddRole
from vrdancing.events.on_database_add import OnAddedToDatabase


async def DBCreateNewMember(user: discord.user):
    name = f"{user.name}#{user.discriminator}"
    # if self.HasMember(user) or self.HasUsername(name):
    #   config.Glogger.Warn(
    #        f"Trying to create member '{user.name}' (Discord id: {user.id}) which already exists!"
    #    )
    #    return

    config.Glogger.Log(f"Creating new member {user.name} (Discord id: {user.id})")
    await config.db.execute(
        """
        INSERT INTO ranks(DiscordID, Username, BootyXP, Rank, DateJoined, Description, Birthday, Country, SwsXP) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        str(user.id),
        name,
        0,
        config.RANK_FITNESS_NEWCOMER,
        datetime.datetime.now().strftime("%d.%m.%Y"),
        f"Your awesome custom description. (Change me with '{config.PREFIX}setdesc')",
        "",
        "",
        False,
    )
    await OnAddedToDatabase(user)


async def DBCreateNewMemberWUsername(user: discord.user, username: str):
    name = f"{user.name}#{user.discriminator}"
    # if self.HasMember(user) or self.HasUsername(name):
    #   config.Glogger.Warn(
    #        f"Trying to create member '{user.name}' (Discord id: {user.id}) which already exists!"
    #    )
    #    return

    config.Glogger.Log(f"Creating new member {user.name} (Discord id: {user.id})")
    await config.db.execute(
        """
        INSERT INTO ranks(DiscordID, Username, BootyXP, Rank, DateJoined, Description, Birthday, Country, SwsXP) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        str(user.id),
        username,
        0,
        config.RANK_FITNESS_NEWCOMER,
        datetime.datetime.now().strftime("%d.%m.%Y"),
        f"Your awesome custom description. (Change me with '{config.PREFIX}setdesc')",
        "",
        "",
        False,
    )
    await OnAddedToDatabase(user)


async def GetDBUserByID(usr: str):
    row = await config.db.fetchrow("SELECT * FROM ranks WHERE discordid = $1", str(usr))
    return row


# async def GetDBUser(self, user: discord.user):
async def GetorCreateDBUser(usr: str, member: discord.user):
    row = await config.db.fetchrow("SELECT * FROM ranks WHERE discordid = $1", usr)
    if row is None:
        await DBCreateNewMemberWUsername(member, member.name)
        return await config.db.fetchrow("SELECT * FROM ranks WHERE discordid = $1", usr)
    else:
        return row


# async def GetDBUser(self, user: discord.user):
async def GetDBUser(usr: str):
    row = await config.db.fetchrow("SELECT * FROM ranks WHERE username = $1", usr)
    return row


async def SetRank(usr: str, rank: str):
    row = await config.db.fetchrow("SELECT * FROM ranks WHERE username = $1", usr)
    await config.db.execute(
        "UPDATE ranks SET rank = $1 WHERE discordid = $2", rank, row["discordid"]
    )


async def SetName(usr: str, user: discord.member):
    await config.db.execute(
        "UPDATE ranks SET username = $1 WHERE discordid = $2", usr, str(user.id)
    )


async def SetDesc(Desc: str, user: discord.member):
    await config.db.execute(
        "UPDATE ranks SET description = $1 WHERE discordid = $2", Desc, str(user.id)
    )


async def SetCountry(Desc: str, user: discord.member):
    await config.db.execute(
        "UPDATE ranks SET country = $1 WHERE discordid = $2", Desc, str(user.id)
    )


async def SetBDay(Desc: str, user: discord.member):
    await config.db.execute(
        "UPDATE ranks SET birthday = $1 WHERE discordid = $2", Desc, str(user.id)
    )


async def resetSWS():
    rows = await config.db.fetch("SELECT * FROM ranks")
    for row in rows:
        if row["swsxp"]:
            await config.db.execute(
                "UPDATE ranks SET swsxp = $1 WHERE discordid = $2",
                False,
                row["discordid"],
            )
            print(row)
        else:
            continue
