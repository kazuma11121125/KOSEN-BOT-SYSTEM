import discord
from discord.ext import commands, tasks
from json import load
from datetime import datetime,timedelta
from discord import app_commands
from student_schedule_manager import ClassScheduleManager,SubmissionManager,ClassuserSystem
from discord import ui


class Questionnaire(ui.Modal, title="教科入力"):
    def __init__(self,mode, class_name):
        super().__init__()
        self.mode = mode
        self.class_name = class_name
        self.schedule_manager = ClassScheduleManager()
         
        self.one = ui.TextInput(label='一限目', style=discord.TextStyle.short,min_length=1)
        self.two = ui.TextInput(label='二限目', style=discord.TextStyle.short,min_length=1)
        self.three = ui.TextInput(label='三限目', style=discord.TextStyle.short,min_length=1)
        self.four = ui.TextInput(label='四限目', style=discord.TextStyle.short,min_length=1)
        self.add_item(self.one)
        self.add_item(self.two)
        self.add_item(self.three)
        self.add_item(self.four)
        
    async def on_submit(self, interaction: discord.Interaction):
        self.data = self.schedule_manager.load_data()
        one = str(self.one)
        two = str(self.two)
        three = str(self.three)
        four = str(self.four)
        if self.class_name in self.data["classes"]:
            base = self.data["classes"][self.class_name]
            new_list = [one,two,three,four]
            base["Basic"][self.mode] = new_list
            await self.schedule_manager.add_class_schedule(self.class_name, base)
            embed = discord.Embed(color=0x2ecc71,title=f"{self.mode} 講義日程")
            cont = 1
            for i in base["Basic"][self.mode]:
                embed.add_field(name=f"{cont}限目",value=i,inline=False)
                cont = cont+1
            await interaction.response.send_message(embed=embed)

class discord_button_model(discord.ui.View):
    def __init__(self, class_name):
        self.clasname = class_name
        super().__init__()

    async def switching(self, interaction, button, mode):
        await interaction.response.send_modal(Questionnaire(mode, self.clasname))

    @discord.ui.button(label="月曜日")
    async def mon(self, button, interaction):
        await self.switching(button, interaction, "Monday")

    @discord.ui.button(label="火曜日")
    async def tus(self, button, interaction):
        await self.switching(button, interaction, "Tuesday")

    @discord.ui.button(label="水曜日")
    async def wes(self, button, interaction):
        await self.switching(button, interaction, "Wednesday")

    @discord.ui.button(label="木曜日")
    async def thu(self, button, interaction):
        await self.switching(button, interaction, "Thursday")

    @discord.ui.button(label="金曜日")
    async def fri(self, button, interaction):
        await self.switching(button, interaction, "Friday")

class schedule_class(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.schedule_manager = ClassScheduleManager()
        self.submission_manager = SubmissionManager()
        self.user_info = ClassuserSystem()

    @app_commands.command()
    async def add_basic(self,interaction):
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            embed = discord.Embed(color=0x2ecc71,title="基本設定")
            await interaction.response.send_message(embed=embed, view=discord_button_model(classname))
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。")


    @app_commands.command()
    async def edit_schedule(self,interaction,target_date:str,period:int,value:str):
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            base = await self.schedule_manager.view_class_schedule(classname,target_date)
            if period < 5:
                period = period -1
                base[period] = value
                await self.schedule_manager.edit_class_schedule(classname, target_date, base)
                await interaction.response.send_message("OK")
            else:
                await interaction.response.send_message(f"ん？？？\nそんな授業数ないお{period}")
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。")


    @app_commands.command()
    async def user_add(self,interaction,classname:str):
        if not await self.user_info.check_user(interaction.user.id):
            await self.user_info.add_user(interaction.user.id,classname)
            await interaction.response.send_message("Ok")
        else:
            await interaction.response.send_message("既に追加済みです")

    
    @app_commands.command()
    async def target_check(self,interaction,date:str):
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            result = await self.schedule_manager.view_class_schedule(classname, date)
            cont = 1
            embed = discord.Embed(color=0x2ecc71,title=f"{date} 講義日程")
            for i in result:
                embed.add_field(name=f"{cont}限目",value=i,inline=False)
                cont = cont+1
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("ユーザー情報が見つかりませんでした。")

async def setup(bot):
    await bot.add_cog(schedule_class(bot))
    print("[SystemLog] スケジュール Cog：ロード完了")