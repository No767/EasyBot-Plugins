# This is the same exact cog found on Rin

import os

import discord
import discord.ext
import qrcode
from discord.ext import commands


class qrcode_maker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="qrcode")
    async def code(self, ctx, *, link: str):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        if str(os.path.isfile("/qrcode/qrcode.png")) == "False":
            img = qrcode.make(link)
            img.save("./qrcode/qrcode.png")
        else:
            img = qrcode.make(link)
            img.save("./qrcode/qrcode.png")
        file = discord.File("./qrcode/qrcode.png")
        embedVar = discord.Embed()
        embedVar.set_image(url="attachment://qrcode.png")
        await ctx.send(embed=embedVar, file=file)

    @code.error
    async def on_message_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.MissingRequiredArgument):
            embedVar = discord.Embed(color=discord.Color.from_rgb(255, 51, 51))
            embedVar.description = f"Missing a required argument: {error.param}"
            msg = await ctx.send(embed=embedVar, delete_after=10)
            await msg.delete(delay=10)


def setup(bot):
    bot.add_cog(qrcode_maker(bot))
