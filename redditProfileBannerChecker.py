from typing import Text
import discord
import requests
import sqlite3
from discord.ext import tasks

responseChannel = 856337987016065048

conn = sqlite3.connect(r"C:\alexmaestroarg_profiledata.db")
c = conn.cursor()

recordedicon = ""
recordedbanner = ""

accounts = ["AlexMaestro", "AveryMasters", "Fac50Log11013"]

c.execute("""CREATE TABLE IF NOT EXISTS users (
    user text, 
    profile_icon text, 
    profile_banner text
    )""")

for user in accounts:
    c.execute("INSERT INTO users VALUES ('{}', 'dummy', 'dummy')".format(user))

c.execute("SELECT * FROM users")

print(c.fetchall())

conn.commit()

headers = {"User-Agent": "JoshumentsBot"}

def grabIcon(user):
    APIGrab = requests.get('https://www.reddit.com/user/{}/about.json'.format(user), headers=headers)
    return APIGrab

@tasks.loop(seconds=30)
async def check():
    for user in accounts:
        jsondata = grabIcon(user).json()
        profileicon = Text.split(jsondata['data']['subreddit']['icon_img'], '?')[0]
        bannericon = Text.split(jsondata['data']['subreddit']['banner_img'], '?')[0]
        c.execute("SELECT profile_icon FROM users WHERE user=:user", {'user':user})
        rawPfpData = c.fetchone()[0]
        c.execute("SELECT profile_banner FROM users WHERE user=:user", {'user':user})
        rawBannerData = c.fetchone()[0]

        if rawPfpData != profileicon:
            channel = client.get_channel(responseChannel)
            c.execute("UPDATE users SET profile_icon = :profile_icon WHERE user = :user", {'profile_icon':profileicon, 'user':user})
            conn.commit()
            await channel.send("@everyone profile picture of {} has changed! Current profile picture: {}".format(user, profileicon))
        if rawBannerData != bannericon:
            channel = client.get_channel(responseChannel)
            c.execute("UPDATE users SET profile_banner = :profile_banner WHERE user = :user", {'profile_banner':bannericon, 'user':user})
            conn.commit()
            await channel.send("@everyone profile banner of {} has changed! Current profile banner: {}".format(user, bannericon))

    c.execute("SELECT * FROM users")
    print(c.fetchall())

class MyClient(discord.Client):
    async def on_ready(self):
        print("bot is running!")
        check.start()

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run('TOKEN HERE')


