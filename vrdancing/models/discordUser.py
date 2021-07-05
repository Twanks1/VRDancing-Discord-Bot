from vrdancing.database.storage import SetRank, GetDBUser
class DiscordUser:
    def __init__(
        self, dcUser, row, id, discordID, username, bootyXP, rank, dateJoined, userDesc
    ):
        row = GetDBUser(username)
        self.discordUser = dcUser  # Can be None if this class was created as read-only (e.g. for top member query)
        self.row = int(row)
        self.id = int(id)
        self.discordID = int(discordID)
        self.name = username
        self.bootyXP = int(bootyXP)
        self.rank = rank
        self.dateJoined = dateJoined
        self.userDesc = userDesc

    async def onRankChange(usr: str, rank: str):
        await SetRank(usr, rank)

        oldRank 