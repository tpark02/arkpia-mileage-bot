import discord
from discord.ext import commands
from pymongo import MongoClient
from datetime import datetime
import time
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_TOKEN = os.environ.get('DB_TOKEN')

cluster = MongoClient(DB_TOKEN)
db = cluster["discord-bot"]
userinfo = db["userinfo"]
loginfo = db["rewardloginfo"]

intents = discord.Intents.all()
client = commands.Bot(intents=intents, command_prefix='/')

@client.tree.command(name = "areward", description = "My first application Command", guild=discord.Object(id=953562711365673000))
@commands.has_role(953565602885304362)
async def areward(inter: discord.Interaction, id : str, amount : int, code : str):
    res = userinfo.find_one({"_id": str(id)})

    if res is None:
        print("No log info " + str(id))
    else:
        current_mileage = res['mileage']
        userinfo.update_one({"_id": str(id)}, {"$set": {"mileage": current_mileage + amount}})

    name = ""
    for m in inter.guild.members:
        if m.id == id:
            name = m.name + "#" + m.discriminator
            break
    loginfo.insert_one({ "userid" : str(id), "name" : name, "amount" : amount, "code" : code })
    await inter.response.send_message(f"userid : {str(id)}, name : {name}, amount : {amount}, code : {code} is inserted.")

@client.tree.command(name = "getmembers", description = "My first application Command", guild=discord.Object(id=953562711365673000))
@commands.has_role(953565602885304362)
async def getmembers(inter):
    print(len(inter.message.guild.members))
    with open('member.txt', 'w', encoding='utf-8') as f:
        for m in inter.message.guild.members:
            #print(str(m.id) + ":" + str(m.name))
            f.write(str(m.name.replace(" ", "_") + "#" + m.discriminator) + "::" + str(m.id) + "\n")

@client.tree.command(name = "atotalrank", description = "My first application Command", guild=discord.Object(id=953562711365673000))
@commands.has_role(953565602885304362)
async def atotalrank(inter):
    users = userinfo.find().sort("mileage", -1)
    em = discord.Embed(title = f"Top 20 Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color.gold())
    for i in range(0, 20):
        name = users[i]["author"]
        mileage = users[i]["mileage"]
        em.add_field(name=f"#{i+1}. { name }", value=f"    { mileage }", inline=False)
    await inter.response.send_message(embed = em)


@client.tree.command(name = "arank", description = "My first application Command", guild=discord.Object(id=953562711365673000))
@commands.has_role(953565602885304362)
async def arank(inter):
    res = userinfo.find_one({"_id": str(inter.user.id) })
    print(str(inter.user.id))
    if res is not None:
        userLevel = res["level"]
        mileage = res["mileage"]

        embed = discord.Embed(
            title="Arkpia Level Status",
            description=f"{ inter.user.name }'s level is {userLevel}. The current mileage is {mileage}.",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
        embed.set_author(name="Arkpia", url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png", icon_url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
        await inter.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Arkpia Level Status",
            description="There is no data",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
        embed.set_author(name="Arkpia", url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png", icon_url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
        await inter.response.send_message(embed=embed)

@client.event
async def on_member_join(member):
    return;
    print("member_join : " + str(member.name))

    if member.id == 863168632941969438 or \
            member.id == 1054290774864429066 or \
            member.id == 159985870458322944:
        return

    user = await member.author.create_dm()

    embed = discord.Embed(
        title="Welcome to Arkpia Point!",
        description="When you chat, you will receive 5 exp! As you level up with exp, for each level, you will be rewarded with Arkpia Mileage! With Arkpia Mileage, you will be able to use it for upcoming Arkpia NFT, events and many more !",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url="https://i.ibb.co/dW7W5Lv/arkpia-symbol.png")
    embed.set_author(name="Arkpia", url="", icon_url="")

    await user.send(embed=embed)
@client.event
async def on_ready():
    await client.tree.sync(guild=discord.Object(id=953562711365673000))
    print("Ready!")

@client.event
async def on_message(message):
    if message.author.id != 1024322879149572156 \
        and message.author.id != 977863630601195540: #tpark#7145 #tpark07#6034
        return

    if message.author == client.user:
        return

    if message.author.id == 863168632941969438 or \
            message.author.id == 1054290774864429066 or \
            message.author.id == 159985870458322944 or \
            message.channel.name == '🥸│verify' or \
            message.channel.name == '👑│about' or \
            message.channel.name == '🔗│official-links' or \
            message.channel.name == '🐤│twitter-raid':
        return

    res = userinfo.find_one({ "_id" : str(message.author.id) })

    if res is None:
        # get current datetime
        today = datetime.now()
        # Get current ISO 8601 datetime in string format
        iso_date = today.isoformat()
        userinfo.insert_one({ "_id" : str(message.author.id), "author" : str(message.author), "level" : 0, "exp" : 0, "mileage" : 0, "msg" : 0, "todayMsg" : 0, "todayExp" : 0, "createdAt" : iso_date })
        print(f"1. New Member Insert id : { message.author.id }, author : { message.author }")
    else:
        exp = res["exp"]
        todayExp = res["todayExp"]
        level_start = res["level"]
        mileage = res["mileage"]
        msgCnt = res["msg"]
        todayMsgCnt = res["todayMsg"]
        # todayLevelUp = res["todayLevelUp"]

        msgCnt = msgCnt + 1;
        todayMsgCnt = todayMsgCnt + 1;
        print(
            f"2. author: {message.author}, todayExp: {todayExp}, exp: {exp}, level_start: {level_start}, mileage: {mileage}")

        if todayExp + 15 <= 200:
            todayExp = todayExp + 15
            exp = exp + 15

            level_end, mile = getLvlMile(exp)
            print(f"2.2. Level Up ! level_start: {level_start} level_end : {level_end}")
            if level_start != level_end:
                print(f"3. Level Up ! level_start: { level_start } level_end : { level_end }")
                # todayLevelUp = 1
                mileage = mileage + mile

            userinfo.update_one({"_id": str(message.author.id) }, {
            "$set": {"exp": exp, \
                     "todayExp": todayExp, \
                     "level": level_end, \
                     "mileage": mileage, \
                     "msg": msgCnt, \
                     "todayMsg": todayMsgCnt}
            })
            print(f"4. author : {str(message.author)}, level_start : {level_start}, leve_end : {level_end}, exp : {exp}, mileage : {mileage}, todayExp : {todayExp}, todayMsg : {todayMsgCnt}")
        else:
            userinfo.update_one({"_id": str(message.author.id) }, {"$set": {"todayMsgCnt": todayMsgCnt }})
            print(f"5. author : {str(message.author)}, todayMsgCnt: {todayMsgCnt}")

    await client.process_commands(message)

def convertTime(t: float):
    d = datetime.fromtimestamp(t)
    print(f"converTime : { d }")
    return d
def getTimeStampNow():
    timestamp = time.mktime(datetime.today().timetuple())
    print(f"time stamp : {timestamp}")
    return timestamp

def getLvlMile(exp):
    level_end = 0
    mileage = 0
    if exp < 100:
        level_end = 0
        mileage += 0
    elif 100 <= exp < 255:
        level_end = 1
        mileage += 2.0
    elif 255 <= exp < 475:
        level_end = 2
        mileage += 2.1
    elif 475 <= exp < 770:
        level_end = 3
        mileage += 2.1
    elif 770 <= exp < 1150:
        level_end = 4
        mileage += 2.2
    elif 1150 <= exp < 1625:
        level_end = 5
        mileage += 2.3
    elif 1625 <= exp < 2205:
        level_end = 6
        mileage += 2.4
    elif 2205 <= exp < 2900:
        level_end = 7
        mileage += 2.5
    elif 2900 <= exp < 3720:
        level_end = 8
        mileage += 2.7
    elif 3720 <= exp < 4675:
        level_end = 9
        mileage += 2.9
    elif 4675 <= exp < 5775:
        level_end = 10
        mileage += 3.2
    elif 5775 <= exp < 7030:
        level_end = 11
        mileage += 3.5
    elif 7030 <= exp < 8450:
        level_end = 12
        mileage += 3.8
    elif 8450 <= exp < 10045:
        level_end = 13
        mileage += 4.2
    elif 10045 <= exp < 11825:
        level_end = 14
        mileage += 4.6
    elif 11825 <= exp < 13800:
        level_end = 15
        mileage += 5.1
    elif 13800 <= exp < 15980:
        level_end = 16
        mileage += 5.7
    elif 15980 <= exp < 18375:
        level_end = 17
        mileage += 6.3
    elif 18375 <= exp < 20995:
        level_end = 18
        mileage += 6.9
    elif 20995 <= exp < 23850:
        level_end = 19
        mileage += 7.7
    elif 23850 <= exp < 26950:
        level_end = 20
        mileage += 8.5
    elif 26950 <= exp < 30305:
        level_end = 21
        mileage += 9.4
    elif 30305 <= exp < 33925:
        level_end = 22
        mileage += 10.3
    elif 33925 <= exp < 37820:
        level_end = 23
        mileage += 11.4
    elif 37820 <= exp < 42000:
        level_end = 24
        mileage += 12.5
    elif 42000 <= exp < 46475:
        level_end = 25
        mileage += 13.8
    elif 46475 <= exp < 51255:
        level_end = 26
        mileage += 15.1
    elif 51255 <= exp < 56350:
        level_end = 27
        mileage += 16.5
    elif 56350 <= exp < 61770:
        level_end = 28
        mileage += 18.0
    elif 61770 <= exp < 67525:
        level_end = 29
        mileage += 19.6
    elif 67525 <= exp < 73625:
        level_end = 30
        mileage += 21.4
    elif 73625 <= exp < 80080:
        level_end = 31
        mileage += 23.2
    elif 80080 <= exp < 86900:
        level_end = 32
        mileage += 25.2
    elif 86900 <= exp < 94095:
        level_end = 33
        mileage += 27.2
    elif 94095 <= exp < 101675:
        level_end = 34
        mileage += 29.4
    elif 101675 <= exp < 109650:
        level_end = 35
        mileage += 31.8
    elif 109650 <= exp < 118030:
        level_end = 36
        mileage += 34.2
    elif 118030 <= exp < 126825:
        level_end = 37
        mileage += 36.8
    elif 126825 <= exp < 136045:
        level_end = 38
        mileage += 39.5
    elif 136045 <= exp < 145700:
        level_end = 39
        mileage += 42.4
    elif 145700 <= exp < 155800:
        level_end = 40
        mileage += 45.4
    elif 155800 <= exp < 166355:
        level_end = 41
        mileage += 48.6
    elif 166355 <= exp < 177375:
        level_end = 42
        mileage += 51.9
    elif 177375 <= exp < 188870:
        level_end = 43
        mileage += 55.4
    elif 188870 <= exp < 200850:
        level_end = 44
        mileage += 59.0
    elif 200850 <= exp < 213325:
        level_end = 45
        mileage += 62.8
    elif 213325 <= exp < 226305:
        level_end = 46
        mileage += 66.8
    elif 226305 <= exp < 239800:
        level_end = 47
        mileage += 70.9
    elif 239800 <= exp < 253820:
        level_end = 48
        mileage += 75.3
    elif 253820 <= exp < 268375:
        level_end = 49
        mileage += 79.8
    elif 268375 <= exp < 283475:
        level_end = 50
        mileage += 84.5
    elif 283475 <= exp < 299130:
        level_end = 51
        mileage += 89.3
    elif 299130 <= exp < 315350:
        level_end = 52
        mileage += 94.4
    elif 315350 <= exp < 332145:
        level_end = 53
        mileage += 99.7
    elif 332145 <= exp < 349525:
        level_end = 54
        mileage += 105.2
    elif 349525 <= exp < 367500:
        level_end = 55
        mileage += 110.8
    elif 367500 <= exp < 386080:
        level_end = 56
        mileage += 116.7
    elif 386080 <= exp < 405275:
        level_end = 57
        mileage += 122.8
    elif 405275 <= exp < 425095:
        level_end = 58
        mileage += 129.1
    elif 425095 <= exp < 445550:
        level_end = 59
        mileage += 135.7
    elif 445550 <= exp < 466650:
        level_end = 60
        mileage += 142.4
    elif 466650 <= exp < 488405:
        level_end = 61
        mileage += 149.4
    elif 488405 <= exp < 510825:
        level_end = 62
        mileage += 156.6
    elif 510825 <= exp < 533920:
        level_end = 63
        mileage += 164.1
    elif 533920 <= exp < 557700:
        level_end = 64
        mileage += 171.8
    elif 557700 <= exp < 582175:
        level_end = 65
        mileage += 179.7
    elif 582175 <= exp < 607355:
        level_end = 66
        mileage += 187.9
    elif 607355 <= exp < 633250:
        level_end = 67
        mileage += 196.4
    elif 633250 <= exp < 659870:
        level_end = 68
        mileage += 205.1
    elif 659870 <= exp < 687225:
        level_end = 69
        mileage += 214.1
    elif 687225 <= exp < 715325:
        level_end = 70
        mileage += 223.3
    elif 715325 <= exp < 744180:
        level_end = 71
        mileage += 232.8
    elif 744180 <= exp < 773800:
        level_end = 72
        mileage += 242.6
    elif 773800 <= exp < 804195:
        level_end = 73
        mileage += 252.7
    elif 804195 <= exp < 835375:
        level_end = 74
        mileage += 263.0
    elif 835375 <= exp < 867350:
        level_end = 75
        mileage += 273.7
    elif 867350 <= exp < 900130:
        level_end = 76
        mileage += 284.6
    elif 900130 <= exp < 933725:
        level_end = 77
        mileage += 295.8
    elif 933725 <= exp < 968145:
        level_end = 78
        mileage += 307.4
    elif 968145 <= exp < 1003400:
        level_end = 79
        mileage += 319.2
    elif 1003400 <= exp < 1039500:
        level_end = 80
        mileage += 331.3
    elif 1039500 <= exp < 1076455:
        level_end = 81
        mileage += 343.8
    elif 1076455 <= exp < 1114275:
        level_end = 82
        mileage += 356.5
    elif 1114275 <= exp < 1152970:
        level_end = 83
        mileage += 369.6
    elif 1152970 <= exp < 1192550:
        level_end = 84
        mileage += 383.1
    elif 1192550 <= exp < 1233025:
        level_end = 85
        mileage += 396.8
    elif 1233025 <= exp < 1274405:
        level_end = 86
        mileage += 410.9
    elif 1274405 <= exp < 1316700:
        level_end = 87
        mileage += 425.3
    elif 1316700 <= exp < 1359920:
        level_end = 88
        mileage += 440.1
    elif 1359920 <= exp < 1404075:
        level_end = 89
        mileage += 455.2
    elif 1404075 <= exp < 1449175:
        level_end = 90
        mileage += 470.6
    elif 1449175 <= exp < 1495230:
        level_end = 91
        mileage += 486.5
    elif 1495230 <= exp < 1542250:
        level_end = 92
        mileage += 502.6
    elif 1542250 <= exp < 1590245:
        level_end = 93
        mileage += 519.2
    elif 1590245 <= exp < 1639225:
        level_end = 94
        mileage += 536.1
    elif 1639225 <= exp < 1689200:
        level_end = 95
        mileage += 553.4
    elif 1689200 <= exp < 1740180:
        level_end = 96
        mileage += 571.0
    elif 1740180 <= exp < 1792175:
        level_end = 97
        mileage += 589.1
    elif 1792175 <= exp < 1845195:
        level_end = 98
        mileage += 607.5
    elif 1845195 <= exp < 1899250:
        level_end = 99
        mileage += 626.3
    elif 1899250 <= exp:
        level_end = 100
        mileage += 645.6
    return level_end, mileage

client.run(BOT_TOKEN)
