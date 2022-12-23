import datetime
import discord
import requests
import random
import math
import re
import os

from discord.ext import commands
from pymongo import MongoClient


cluster = MongoClient(f"mongodb+srv://tpark01:1234@cluster0.vrj8l.mongodb.net/discord-bot?retryWrites=true&w=majority")
db = cluster["discord-bot"]

userinfo = db["userinfo"]
servers = db["servers"]

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix='p!')

TOKEN = os.environ.get('BOT_TOKEN')

@client.command()
async def level(ctx):
    res = userinfo.find_one({"_id": ctx.author.id})
    if res is not None:
        userLevel = res["level"]
        mileage = res["mileage"]

        await ctx.send(f"{ctx.author}'s level is {userLevel}. The current mileage is {mileage}.")
    else:
        await ctx.send(f"There is no data of {ctx.author}.")

@client.event
async def on_member_join(member):
    print("member_join : " + str(member.name))

    if member.id == 863168632941969438 or \
            member.id == 1054290774864429066 or \
            member.id == 159985870458322944:
        return
    #if member.id != 946318480272130078 and member.id != 977863630601195540:
    #    return

    embed = discord.Embed(
        title="Welcome to Arkpia Point!",
        description="When you chat, you will receive 5 exp! As you level up with exp, for each level, you will be rewarded with Arkpia Mileage! With Arkpia Mileage, you will be able to use it for upcoming Arkpia NFT, events and many more !",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
    embed.set_author(name="Arkpia", url="", icon_url="")

    await member.send(embed=embed)

@client.event
async def on_message(message):
    print("on_message : " + str(message.author.id) + " : " + str(message.author))

    if message.author == client.user:
        return

    if message.author.id == 863168632941969438 or \
            message.author.id == 1054290774864429066 or \
            message.author.id == 159985870458322944:
        return
    #if message.author.id != 946318480272130078 and message.author.id != 977863630601195540:
    #    return

    # print("jnjohn id : " + str(message.guild.id))
    # print("channel id : " + str(message.channel.id))
    # print("user id : " + str(message.author.id))

    res = userinfo.find_one({ "_id" : message.author.id })
    # print(res)

    if res is None:
        userinfo.insert_one({ "_id" : message.author.id, "author" : str(message.author), "level" : 1, "exp" : 0, "mileage" : 3})
    else:
        exp = res["exp"]
        level_start = res["level"]
        level_end = int(exp ** (1 / 4))
        mileage = res["mileage"]

        userinfo.update_one({ "_id" : message.author.id }, {"$set" : { "exp" : exp + 5 }})

        print(f" _id : { str(message.author) }, level_start : { level_start }, leve_end : { level_end }, mileage : { mileage }")

        if level_start < level_end:
            if 1 <= level_end < 5:
                mileage += 50
            elif 5 <= level_end < 10:
                mileage += 30
            elif 10 <= level_end:
                mileage += 10

            userinfo.update_one({ "_id": message.author.id }, {"$set" : {"level": level_end, "mileage" : mileage }})

            # user = await message.author.create_dm()
            embed = discord.Embed(
                title="Level Up !",
                description=f"{ str(message.author) } leveled up !! Your level is now { level_end }.",
                color=discord.Color.gold()
            )

            embed.set_thumbnail(url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
            embed.set_author(name="Arkpia", url="", icon_url="")
            # await user.send(embed=embed)
            await message.channel.send(embed=embed)
        else:
            pass
            # await message.channel.send(
            #     f"{ message.author.mention } Not leveled up { str(message.author.id) }. The current level is { level_start }")

    await client.process_commands(message)

client.run(TOKEN)