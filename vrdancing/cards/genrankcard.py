import discord
import config
import io
from PIL import Image, ImageDraw, ImageFont
from vrdancing.utils.image_utils import ImageText
from vrdancing.database.storage import GetDBUserByID
from vrdancing.utils.check_rank import RankIndex
from vrdancing.events import rankupdate
async def Lerp(a, b, val):
    if val > 1:
        val = 1
    if val <= 0:
        val = 0
    return (val * b) + ((1 - val) * a)


async def GenerateRankCard( user: discord.Member):
        row = await GetDBUserByID(user.id)
        currentRankIndex = RankIndex(row['rank'])
        bMaxLevel = currentRankIndex == len(config.gRanks)-1

        rankCur  = config.gRanks[currentRankIndex]
        rankNext = config.gRanks[min(currentRankIndex + 1, len(config.gRanks)-1)]

        username       = row['username']                    
        currentXP      = row['bootyxp']
        currentRank    = rankCur.name
        nextRank       = rankNext.name
        XPCurrentLevel = rankCur.requiredPoints
        XPNextLevel    = rankNext.requiredPoints                    
        rankColor      = rankCur.color
        nextRankColor  = rankNext.color
            
        # Image
        w, h = 1024, 256
        img = Image.new("RGBA", (w, h), "#090A0B")
        draw = ImageDraw.Draw(img)            

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        # Progress Bar
        progressBarStart = (286, 180)
        progressBarEnd = (984, 230)
        progressBarHeight = progressBarEnd[1] - progressBarStart[1]
        draw.rectangle([progressBarStart,progressBarEnd], fill=(72, 75, 78))
        percentageToNextLevel = 1 if bMaxLevel else (currentXP - XPCurrentLevel)/(XPNextLevel - XPCurrentLevel)
        if percentageToNextLevel > 0:
            draw.rectangle([progressBarStart, (progressBarStart[0] + percentageToNextLevel*(progressBarEnd[0]-progressBarStart[0]), progressBarEnd[1])], fill=rankColor) 

        textAboveProgressBarY = progressBarStart[1] - 20
        textAboveProgressBarMargin = 25

        # Rank
        fontPathForText = "fonts/CutieShark.ttf"
        fnt = ImageFont.truetype(fontPathForText, 70)
        strRank = f"{currentRank}"
        sw, sh = draw.textsize(strRank, fnt)
        rankTextY = sh
        draw.text((w - 20, rankTextY), strRank, font=fnt, fill=rankColor, align="right", anchor="rs")

        fnt = ImageFont.truetype(fontPathForText, 40)
        draw.text((w - 50 - sw, rankTextY), f"Rank # {await rankupdate.GetXP(row['username'])}", font=fnt, fill="#6C7071", align="right", anchor="rs")

        # Username
        usernameLenMaxPercent = len(username) / config.MAXLENUSERNAME
        usernameFontSize = int(await Lerp(25, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
        fnt = ImageFont.truetype("fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf", usernameFontSize) # Unicode font which contains special characters like ღὣ
        draw.text((progressBarStart[0] + textAboveProgressBarMargin, textAboveProgressBarY), f"{username}", font=fnt, fill=rankColor, anchor="ls")

        # XP
        fnt = ImageFont.truetype(fontPathForText, 30)
        bootyXPStr = f"/ {XPNextLevel} Booty XP"
        draw.text((progressBarEnd[0] - textAboveProgressBarMargin, textAboveProgressBarY), bootyXPStr, font=fnt, fill="#6C7071", align="right", anchor="rs")
        
        sw, sh = draw.textsize(bootyXPStr, fnt)
        draw.text((progressBarEnd[0] - textAboveProgressBarMargin - sw - 10, textAboveProgressBarY), f"{currentXP}", font=fnt, fill="#FFFFFF", align="right", anchor="rs")

        # Next Rank
        fnt = ImageFont.truetype(fontPathForText, 40)
        draw.text((progressBarEnd[0] - 10, progressBarEnd[1] - progressBarHeight/2), f"{nextRank}", font=fnt, fill=nextRankColor, align="right", anchor="rm")

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")