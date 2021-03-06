import math
import os
import random

import discord
from discord.ext import commands
from sqlalchemy import (Column, Integer, MetaData, Table, create_engine, func,
                        select, BigInteger, Sequence)
from sqlalchemy.ext.asyncio import create_async_engine


class helper:
    def fast_embed(content):
        colors = [0x8B77BE, 0xA189E2, 0xCF91D1, 0x5665AA, 0xA3A3D2]
        selector = random.choice(colors)
        return discord.Embed(description=content, color=selector)


class disaccount:
    def __init__(self, ctx):
        self.id = ctx.author.id
        self.gid = ctx.guild.id

    async def getxp(self):
        meta = MetaData()
        engine = create_async_engine("sqlite+aiosqlite:///disquest/user.db")
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
        async with engine.connect() as conn:
            s = select(users.c.xp).where(
                users.c.id == self.id, users.c.gid == self.gid)
            results = await conn.execute(s)
            results_fetched = results.fetchone()
            if results_fetched is None:
                insert_new = users.insert().values(xp=0, id=self.id, gid=self.gid)
                await conn.execute(insert_new)
            else:
                for row in results_fetched:
                    return row

    async def setxp(self, xp):
        meta = MetaData()
        engine = create_async_engine(
            "sqlite+aiosqlite:///disquest/user.db"
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
        async with engine.begin() as conn:
            update_values = (
                users.update()
                .values(xp=xp)
                .filter(users.c.id == self.id)
                .filter(users.c.gid == self.gid)
            )
            await conn.execute(update_values)

    async def addxp(self, offset):
        pxp = await self.getxp()
        pxp += offset
        await self.setxp(pxp)


class lvl:
    def near(xp):
        return round(xp / 100)

    def next(xp):
        return math.ceil(xp / 100)

    def cur(xp):
        return int(xp / 100)


class DisQuest(commands.Cog):
    async def __init__(self, bot):
        self.bot = bot
        os.chdir(os.path.dirname(__file__))
        meta = MetaData()
        engine = create_async_engine(
            "sqlite+aiosqlite:///disquest/user.db"
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
        async with engine.connect() as conn:
            await conn.run_sync(meta.create_all)

    @commands.command(
        name="mylvl",
        help="Displays your activity level!",
    )
    async def mylvl(self, ctx):
        user = disaccount(ctx)
        xp = await user.getxp()
        embedVar = discord.Embed(color=discord.Color.from_rgb(255, 217, 254))
        embedVar.add_field(
            name="User", value=f"{ctx.author.mention}", inline=True)
        embedVar.add_field(name="LVL", value=f"{lvl.cur(xp)}", inline=True)
        embedVar.add_field(
            name="XP", value=f"{xp}/{lvl.next(xp)*100}", inline=True)
        await ctx.send(embed=embedVar)

    @commands.command(
        name="rank", help="Displays the most active members of your server!"
    )
    async def rank(self, ctx):
        gid = ctx.guild.id
        meta = MetaData()
        engine = create_async_engine(
            "sqlite+aiosqlite:///disquest/user.db"
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
        async with engine.connect() as conn:
            s = (
                select(Column("id", BigInteger), Column("xp", Integer))
                .where(users.c.gid == gid)
                .order_by(users.c.xp.desc())
            )
            results = await conn.execute(s)
            members = list(results.fetchall())
            for i, mem in enumerate(members):
                members[
                    i
                ] = f"{i}. {(await self.bot.fetch_user(mem[0])).name} | XP. {mem[1]}\n"
            embedVar = discord.Embed(
                color=discord.Color.from_rgb(254, 255, 217))
            embedVar.description = f"**Server Rankings**\n{''.join(members)}"
            await ctx.send(embed=embedVar)

    @commands.command(
        name="globalrank",
        help="Displays the most active members of all servers that this bot is connected to!",
    )
    async def grank(self, ctx):
        meta = MetaData()
        engine = create_async_engine(
            "sqlite+aiosqlite:///disquest/user.db"
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
        async with engine.connect() as conn:
            s = (
                select(Column("id", Integer), func.sum(
                    users.c.xp).label("txp"))
                .group_by(users.c.id)
                .group_by(users.c.xp)
                .order_by(users.c.xp.desc())
                .limit(10)
            )
            results = await conn.execute(s)
            results_fetched = results.fetchall()
            members = list(results_fetched)
            for i, mem in enumerate(members):
                members[
                    i
                ] = f"{i}. {(await self.bot.fetch_user(mem[0])).name} | XP. {mem[1]}\n"
            embedVar = discord.Embed(
                color=discord.Color.from_rgb(217, 255, 251))
            embedVar.description = f"**Global Rankings**\n{''.join(members)}"
            await ctx.send(embed=embedVar)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        user = disaccount(ctx)
        reward = random.randint(0, 20)
        await user.addxp(reward)


def setup(bot):
    bot.add_cog(DisQuest(bot))
