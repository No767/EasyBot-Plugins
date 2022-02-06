from tkinter import *
from discord.ext import commands
import discord
import random
import asyncpraw

class reddit(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="meme",
        help="finds a meme"
    )
    async def meme(self, ctx):
        searchtopics = [' ', 'dank', 'anime', 'christian', 'tech ', 'funny ', 'coding ', 'reddit ', 'music ',
        'manga ', 'school ', 'relatable ']
        searchterm = random.choice(searchtopics) + 'memes'
        await ctx.invoke(self.bot.get_command('reddit'), search = searchterm)

    @commands.command(
        name="reddit",
        help="browses on reddit"
    )
    async def reddit(self, ctx, *, search: str):
        async with asyncpraw.Reddit(client_id="INSERT CLIENTID", client_secret="INSERT CLIENTSECRET", user_agent="Discord)") as api:
            original_search = search
            try:
                if "r/" in search: 
                    search = search.split("/")
                    sub = search[1]
                    search = "all"
                else:
                    sub = "all"
                sub = await api.subreddit(sub)
                searcher = sub.search(query=search)
                posts = [
                    post
                    async for post in searcher
                    if ".jpg" in post.url
                       or ".png" in post.url
                       or ".gif" in post.url
                       and not post.over_18
                ]
                post = random.choice(posts)
                submission = post
                reddit_embed = discord.Embed(
                    color=discord.Color.from_rgb(255, 69, 0))
                reddit_embed.description = f"{self.bot.user.name} found this post in r/{submission.subreddit.display_name} by {submission.author.name} when searching {original_search}"
                reddit_embed.set_image(url=submission.url)
                await ctx.send(embed=reddit_embed)
            except:
                await ctx.send(f'There was an error, this is likely caused by a lack of posts found in the query {original_search}. Please try again.')

def setup(bot):
    bot.add_cog(reddit(bot))
