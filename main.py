from discord.ext import commands
import sys
import discord
import datetime
import os
import json
from discord_schedule_system_class import DiscordButtonModel_disbord
os.chdir(os.path.dirname(os.path.abspath(__file__)))


COGS = [
    # "COGS.schedule",
    # "COGS.homework",
    "jishaku",
    # "COGS.youtube"
    "memorization_maker_view_discord",
    "memorization_maker_add_discord",
]

class MyBot(commands.Bot):
    def __init__(self, prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=prefix, intents=intents)
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="/help"))
        for cog in COGS:
            await bot.load_extension(cog)
        await self.tree.sync()
        dt_now = datetime.datetime.now()
        print("-----------------------")
        print(f"{self.user.display_name}が起動しました ")
        print(dt_now.strftime('%Y-%m-%d %H:%M'))
        print("-----------------------")
        print(discord.version_info)
        print(sys.version)
        print("-----------------------")
        for guild in self.guilds:
            print(guild.name)

        print(f"導入数 {(len(self.guilds))}")
        print("-----------------------")
        await bot.get_channel(1175352758904307792).send("ダッシュボードβ",view = DiscordButtonModel_disbord())
#1175352758904307792 test
#1195565220408610828 honban
bot = MyBot(intents=discord.Intents.all(), prefix='k!')

if __name__ == '__main__':
    with open("token.json", 'r', encoding='utf-8') as file:
        t = json.load(file)
        TOKEN = t["TOKEN"]
    bot.run(token=TOKEN)