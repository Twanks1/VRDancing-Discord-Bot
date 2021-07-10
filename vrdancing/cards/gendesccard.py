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

    
async def GenerateDescCard(user: discord.Member):
        member = await GetDBUserByID(str(user.id))

        # creating Image object
        w, h = 1024, 256
        img = ImageText((w, h), background="#090A0B")                  

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        currentRankIndex = RankIndex(member['rank'])

        rankCur  = config.gRanks[currentRankIndex]
        rankNext = config.gRanks[min(currentRankIndex + 1, len(config.gRanks)-1)]

        username    = member['username']
        currentRank = rankCur.name                  
        rankColor   = rankCur.color

        x = 280
        usernameFont = "fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf"

        # Username
        y = 60
        unamelength = config.MAXLENUSERNAME
        usernameLenMaxPercent = len(username) / unamelength
        usernameFontSize = int(await Lerp(30, 60, (1 - usernameLenMaxPercent))) # Scale font size by username len otherwise it can be too big
        img.write_text(x, y, text=username, font_filename=usernameFont, font_size=usernameFontSize, color=rankColor, anchor="lb")

        # Rank
        fontRank = "fonts/CutieShark.ttf"
        img.write_text(1024 - 10, 35, text=currentRank, font_filename=fontRank, font_size="fill", max_height=35, color=rankColor, anchor="rs")

        # Joined the server date
        try:
            dateJoined = user.joined_at.strftime("%d.%m.%Y")
            img.write_text(1024 - 10, 55, text=f"Joined {dateJoined}", font_filename=fontRank, font_size="fill", max_height=20, color="#6C7071", anchor="rs")
        except:
            pass # Command was called in private bot dm so no join date exists

        # Description
        y = y + 8
        rightMargin = 15
        bottomMargin = 10
        boxWidth = w - x - rightMargin
        boxHeight = h - y - bottomMargin    
        descriptionFont = "fonts/seguiemj.ttf"
        img.write_text_box_fit(x, y, text=member['description'], box_width=boxWidth, box_height=boxHeight, max_font_size = 30, font_filename=descriptionFont, color="#2FD0AA", embedded_color=True)

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")