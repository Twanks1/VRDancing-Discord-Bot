import discord
from PIL import Image, ImageDraw, ImageFont
from vrdancing.utils.image_utils import ImageText
async def GenerateJoinServerCard(self, user: discord.Member):
        # creating Image object
        w, h = 1024, 256
        img = Image.new("RGBA", (w, h), "#090A0B")
        draw = ImageDraw.Draw(img)                    

        # Avatar image
        avatar = await user.avatar_url.read()
        avatarBytes = io.BytesIO(avatar)
        avatarImage = Image.open(avatarBytes).convert("RGBA")
        avatarImage = avatarImage.resize((256, 256))
        img.alpha_composite(avatarImage)

        username = user.name
        discriminator = f"#{user.discriminator}"

        x, y = 350, 128

        # Username
        fnt = ImageFont.truetype("fonts/CutieShark.ttf" if username.isascii() else "fonts/code2000.ttf", 80) # Unicode font which contains special characters like ღὣ
        draw.text((x, y), username, font=fnt, fill="#D0AA2F", align="right", anchor="ls")

        sw, sh = draw.textsize(username, fnt)
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 40) # Unicode font which contains special characters like ღὣ
        draw.text((x + sw, y), discriminator, font=fnt, fill="#6C7071", anchor="ls")

        # Has joined the server text
        textY = y + 45
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 25)
        strJoined = f"has joined the Booty Army. You are booty "
        draw.text((x, textY), strJoined, font=fnt, fill="#2FD0AA", anchor="ls")

        # Nth booty member
        sw, sh = draw.textsize(strJoined, fnt)
        fnt = ImageFont.truetype("fonts/CutieShark.ttf", 45)
        strJoined = f"#{len(gVRdancing.guild.members)}"
        draw.text((x + sw, textY), strJoined, font=fnt, fill="#AA2FD0", anchor="ls")

        arr = io.BytesIO()
        img.save(arr, format='PNG')
        arr.seek(0)
        return discord.File(arr, "card.png")