import config
import discord
from discord.utils import get

async def AddRoles( user: discord.Member, roles):
    for role in roles:
        await AddRole(user, role)


async def AddRole(ctx, user: discord.Member, roleNameOrId):
    try:
        role = GetRole(ctx, roleNameOrId)
        await user.add_roles(role)
    except:
        config.Glogger.Warn(
            f"Failed to add role [{roleNameOrId}] to {str} (Role doesn't exist?)"
        )

async def RemoveRole(ctx, user: discord.Member, roleNameOrId):
    try:
        role = GetRole(ctx, roleNameOrId)
        await user.remove_roles(role)
    except:
        config.Glogger.Warn(f"Failed to remove role [{roleNameOrId}] to {user.name} (Role doesn't exist?)")

def GetRole(ctx, roleNameOrId):
    if isinstance(roleNameOrId, str):
        return get(ctx.guild.roles, name=roleNameOrId)
    else:
        return get(ctx.guild.roles, id=roleNameOrId)