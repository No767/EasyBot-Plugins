import math
import os
import random

import discord
from discord.ext import commands
from sqlalchemy import (Column, Integer, MetaData, Table, create_engine, func,
                        select, BigInteger, Sequence)
from dotenv import load_dotenv


load_dotenv()

# Create an .env file and make sure that the environment variables are set to the exact
# names within the strings

Password = os.getenv("Postgres_Password")
IP = os.getenv("Postgres_Server_IP")
Username = os.getenv("Postgres_Username")

# This version uses PostgreSQL as the backend database
# The reason why is that SQLite3 locks up very fast and is not recommended for cogs like these, where high read/write speeds are key
# Make sure to have an PostgreSQL server running, and a database called "disquest"

class helper:
    def fast_embed(content):
        colors = [0x8B77BE, 0xA189E2, 0xCF91D1, 0x5665AA, 0xA3A3D2]
        selector = random.choice(colors)
        return discord.Embed(description=content, color=selector)


class disaccount:
    def __init__(self, ctx):
        self.id = ctx.author.id
        self.gid = ctx.guild.id

    def getxp(self):
        meta = MetaData()
        engine = create_engine(
            f"postgresql+psycopg2://{Username}:{Password}@{IP}:5432/disquest"
        )
        users = Table(
            "user",
            meta,
            Column(
                "tracking_id",
                Integer,
                Sequence("tracking_id"),
                primary_key=True,
                autoincrement=True,
            ),
            Column("id", BigInteger),
            Column("gid", BigInteger),
            Column("xp", Integer),
        )
        conn = engine.connect()
        s = select(users.c.xp).where(
            users.c.id == self.id, users.c.gid == self.gid)
        results = conn.execute(s).fetchone()
        if results is None:
            insert_new = users.insert().values(xp=0, id=self.id, gid=self.gid)
            conn.execute(insert_new)
        else:
            for row in results:
                return row
        conn.close()

    def setxp(self, xp):
        meta = MetaData()
        engine = create_engine(
            f"postgresql+psycopg2://{Username}:{Password}@{IP}:5432/disquest"
        )
        users = Table(
            "user",
            meta,
            Column(
                "tracking_id",
                Integer,
                Sequence("tracking_id"),
                primary_key=True,
                autoincrement=True,
            ),
            Column("id", BigInteger),
            Column("gid", BigInteger),
            Column("xp", Integer),
        )
        conn = engine.connect()
        update_values = (
            users.update()
            .values(xp=xp) 
            .filter(users.c.id == self.id) # check for the row that contains the user id and guild id
            .filter(users.c.gid == self.gid) # to prevent overwritting the whole xp column
        )
        conn.execute(update_values)
        conn.close()

    def addxp(self, offset):
        pxp = self.getxp()
        pxp += offset
        self.setxp(pxp)


class lvl:
    def near(xp):
        return round(xp / 100)

    def next(xp):
        return math.ceil(xp / 100)

    def cur(xp):
        return int(xp / 100)


class DisQuest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.chdir(os.path.dirname(__file__))
        meta = MetaData()
        engine = create_engine(
            f"postgresql+psycopg2://{Username}:{Password}@{IP}:5432/disquest"
        )
        Table(
            "user",
            meta,
            Column(
                "tracking_id",
                Integer,
                Sequence("tracking_id"),
                primary_key=True,
                autoincrement=True,
            ),
            Column("id", BigInteger),
            Column("gid", BigInteger),
            Column("xp", Integer),
        )
        meta.create_all(engine)

    @commands.command(
        name="mylvl",
        help="Displays your activity level!",
    )
    async def mylvl(self, ctx):
        user = disaccount(ctx)
        xp = user.getxp()
        await ctx.channel.send(
            embed=helper.fast_embed(
                f"""User: {ctx.author.mention}
        LVL. {lvl.cur(xp)}
        XP {xp}/{lvl.next(xp)*100}"""
            )
        )

    @commands.command(
        name="rank", help="Displays the most active members of your server!"
    )
    async def rank(self, ctx):
        gid = discord.Guild.id
        meta = MetaData()
        engine = create_engine(
            f"postgresql+psycopg2://{Username}:{Password}@{IP}:5432/disquest"
        )
        users = Table(
            "user",
            meta,
            Column(
                "tracking_id",
                Integer,
                Sequence("tracking_id"),
                primary_key=True,
                autoincrement=True,
            ),
            Column("id", BigInteger),
            Column("gid", BigInteger),
            Column("xp", Integer),
        )
        conn = engine.connect()
        s = (
            select(Column("id", BigInteger), Column("xp", Integer))
            .where(users.c.gid == gid)
            .order_by(users.c.xp.desc())
        )
        results = conn.execute(s)
        members = list(results.fetchall())
        for i, mem in enumerate(members):
            members[
                i
            ] = f"{i}. {(await self.bot.fetch_user(mem[0])).name} | XP. {mem[1]}\n"
        await ctx.send(
            embed=helper.fast_embed(f"**Server Rankings**\n{''.join(members)}")
        )

    @commands.command(
        name="globalrank",
        help="Displays the most active members of all servers that this bot is connected to!",
    )
    async def grank(self, ctx):
        meta = MetaData()
        engine = create_engine(
            f"postgresql+psycopg2://{Username}:{Password}@{IP}:5432/disquest"
        )
        users = Table(
            "user",
            meta,
            Column(
                "tracking_id",
                Integer,
                Sequence("tracking_id"),
                primary_key=True,
                autoincrement=True,
            ),
            Column("id", BigInteger),
            Column("gid", BigInteger),
            Column("xp", Integer),
        )
        conn = engine.connect()
        s = (
            select(Column("id", Integer), func.sum(users.c.xp).label("txp"))
            .group_by(users.c.id)
            .group_by(users.c.xp)
            .order_by(users.c.xp.desc())
        )
        results = conn.execute(s).fetchall()
        members = list(results)
        for i, mem in enumerate(members):
            members[
                i
            ] = f"{i}. {(await self.bot.fetch_user(mem[0])).name} | XP. {mem[1]}\n"
        await ctx.send(
            embed=helper.fast_embed(f"**Global Rankings**\n{''.join(members)}")
        )

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        user = disaccount(ctx)
        reward = random.randint(0, 20)
        user.addxp(reward)
        xp = user.getxp()
        if lvl.near(xp) * 100 in range(xp - reward, xp):
            await ctx.channel.send(
                embed=helper.fast_embed(
                    f"{ctx.author.mention} has reached LVL. {lvl.cur(xp)}"
                ),
                delete_after=10,
            )


def setup(bot):
    bot.add_cog(DisQuest(bot))
