import csv
from anyio import run
import asyncpg as db

DATABASE_INFORMATION = {  # Database configuration
    "host": "10.1.10.14",  # Host ip of the Database
    "port": 5432,  # Host port of the Database
    "database": "vrdancing",  # Database for the bot
    "user": "vrdancing",  # User of the Database client
    "password": "s6EcghaS7mqGpK",  # Password of the Database client
    "min_size": 30,  # ignore
    "max_size": 50,  # ignore
    "max_inactive_connection_lifetime": 15,  # ignore
}

async def main():
    database = await db.create_pool(**DATABASE_INFORMATION)
    with open("VRDancing - Database.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            print(f"Creating new member {row[2]} (Discord id: {row[1]})")
            await database.execute(
                """
               INSERT INTO ranks(DiscordID, Username, BootyXP, Rank, DateJoined, Description, Birthday, Country, SwsXP) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                row[1],
                row[2],
                int(row[3]),
                row[4],
                row[5],
                row[6],
                "",
                "",
                False,
            )
    print(f"Processed {line_count} lines.")

run(main)