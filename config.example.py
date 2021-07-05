import logging
from vrdancing.other.logger import Logger
from vrdancing.models.rank import Rank



##CHANNELS
RANK_UP = 845509198741897236
RANKS = 782395929654591499
INTRODUCTION = 782374351315533834
SELF_ROLES = 788134961223041054
SWEATSESSION = 781930766111997982
RULES = 781188979374030869
SWEATSESSION_PREP = 850406295647158274

LOCKXP = True  # If mods can use all xp gain commands
MAXXPGAIN = 40  # Max XP which can be added via addBootXP command
MINLENUSERNAME = 3  # Min length of Username
MAXLENUSERNAME = 25  # Max length of Username
NEWUSERDM = True  # Send out new user DM
MINLENDESC = 4  # Min length of Description
MAXLENDESC = 1000  # Max Length of Description
LISTENTOALLMESSAGES = True  # Whether the bot listens to all messages (EasterEggs)

BOT_DESCRIPTION = "A wholesome bot for our VRDancing Discord Server!"
CMD_PREFIX = "$"
GSHEET_FOLDER = "gsheet/"
LOG_LEVEL = logging.INFO
SPLIT_CHAR = (
    ";"  # Split character for giving sweatsession xp to users e.g. "NAME1;NAME2;NAME3"
)

ROLE_ADMIN = "Admin"
ROLE_MODERATOR = "Moderator"
ROLE_FITNESS_INSTRUCTOR = "Fitness Instructor"

ROLE_SPLIT_OTHER_ROLES = "»»       Other Roles       ««"
ROLE_SPLIT_SPECIAL_ROLES = "»»      Special Roles     ««"

XP_LOCK_MSG = "XP gain is currently locked. Contact any admin to ask for unlock."

XP_SWEATSESSION = 10
XP_INSTRUCTOR = 20
XP_BASIC_VIDEO = 20
XP_YT_VIDEO = 40

RANK_FITNESS_NEWCOMER = "Fitness Newcomer"
RANK_FITNESS_CADET = "Fitness Cadet"
RANK_FITNESS_ROOKIE = "Fitness Rookie"
RANK_FITNESS_MAJOR = "Fitness Major"
RANK_FITNESS_OFFICER = "Fitness Officer"
RANK_FITNESS_GENERAL = "Fitness General"
RANK_FITNESS_CAPTAIN = "Fitness Captain"
RANK_FITNESS_COMMANDER = "Fitness Commander"
RANK_FITNESS_ADMIRAL = "Fitness Admiral"
RANK_FITNESS_COMMODORE = "Fitness Commodore"
RANK_FITNESS_MARSHALL = "Fitness Marshall"
RANK_FITNESS_MARSHALL2 = "Fitness Marshall II"
RANK_FITNESS_MARSHALL3 = "Fitness Marshall III"
RANK_FITNESS_GOD = "Fitness God"

## Rank definition
gRanks = [
    Rank(RANK_FITNESS_NEWCOMER, 0, "#ffffff"),
    Rank(RANK_FITNESS_CADET, 10, "#607d8b"),
    Rank(RANK_FITNESS_ROOKIE, 40, "#1f8b4c"),
    Rank(RANK_FITNESS_MAJOR, 80, "#2ecc71"),
    Rank(RANK_FITNESS_OFFICER, 150, "#206694"),
    Rank(RANK_FITNESS_GENERAL, 250, "#3498db"),
    Rank(RANK_FITNESS_CAPTAIN, 350, "#71368a"),
    Rank(RANK_FITNESS_COMMANDER, 500, "#9b59b6"),
    Rank(RANK_FITNESS_ADMIRAL, 650, "#a84300"),
    Rank(RANK_FITNESS_COMMODORE, 800, "#e67e22"),
    Rank(RANK_FITNESS_MARSHALL, 1000, "#f1c40f"),
    Rank(RANK_FITNESS_MARSHALL2, 2000, "#f1c40f"),
    Rank(RANK_FITNESS_MARSHALL3, 5000, "#f1c40f"),
    Rank(RANK_FITNESS_GOD, 10000, "#f1c40f"),
]
# what does this refrence
# default of logging is WARNING, not INFO afaik

logging.basicConfig(level=logging.INFO)
Glogger = Logger("vrdancing", LOG_LEVEL)
TOKEN = ""
PREFIX = "$"  # Prefix of the bot

DATABASE_INFORMATION = {  # Database configuration
    "host": "",  # Host ip of the Database
    "port": 5432,  # Host port of the Database
    "database": "",  # Database for the bot
    "user": "",  # User of the Database client
    "password": "",  # Password of the Database client
    "min_size": 30,  # ignore
    "max_size": 50,  # ignore
    "max_inactive_connection_lifetime": 15,  # ignore
}