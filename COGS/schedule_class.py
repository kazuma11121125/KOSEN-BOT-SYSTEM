import discord
from discord.ext import commands, tasks
from json import load
from datetime import datetime,timedelta
from discord import app_commands
from student_schedule_manager import ClassScheduleManager,SubmissionManager,ClassuserSystem
from discord import ui


class Questionnaire(ui.Modal, title="教科入力"):
    def __init__(self, mode, class_name):
        super().__init__()
        self.mode = mode
        self.class_name = class_name
        self.schedule_manager = ClassScheduleManager()

        self.inputs = [
            ui.TextInput(label='一限目', style=discord.TextStyle.short, min_length=1),
            ui.TextInput(label='二限目', style=discord.TextStyle.short, min_length=1),
            ui.TextInput(label='三限目', style=discord.TextStyle.short, min_length=1),
            ui.TextInput(label='四限目', style=discord.TextStyle.short, min_length=1),
        ]

        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        data = self.schedule_manager.load_data()
        one, two, three, four = [str(input_item) for input_item in self.inputs]

        if self.class_name in data["classes"]:
            base = data["classes"][self.class_name]
        else:
            # If self.class_name is not present, create a new entry
            base = {"Basic": {self.mode: []}}
            data["classes"][self.class_name] = base

        new_list = [one, two, three, four]
        base["Basic"][self.mode] = new_list

        await self.schedule_manager.add_class_schedule(self.class_name, base)

        embed = discord.Embed(color=0x2ecc71, title=f"{self.mode} 講義日程")
        for cont, schedule_item in enumerate(base["Basic"][self.mode], start=1):
            embed.add_field(name=f"{cont}限目", value=schedule_item, inline=False)

        await interaction.response.send_message(embed=embed)

class HomeworkAdd(ui.Modal, title="課題追加"):
    def __init__(self, classname):
        super().__init__()
        self.classname = classname
        self.submission_manager = SubmissionManager()
        self.date = ui.TextInput(label="日付設定(例 2023-12-12) 指定記述方式以外で入力しないで", style=discord.TextStyle.short)
        self.name = ui.TextInput(label="詳細", style=discord.TextStyle.paragraph)
        self.add_item(self.date)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        data = self.submission_manager.load_data()
        date = str(self.date)
        name = str(self.name)

        if self.classname in data["submissions"]:
            try:
                base = data["submissions"][self.classname][date]
            except KeyError:
                base = []
        else:
            base = {"submissions": {self.classname: []}}
            data["submissions"][self.classname] = base

        base.append(name)
        await self.submission_manager.add_submission(self.classname, date, base)
            
        await interaction.response.send_message("add homework ok")

class DiscordButtonModel(discord.ui.View):
    def __init__(self, class_name):
        self.classname = class_name
        super().__init__()

    async def switching(self, interaction: discord.Interaction, button, mode):
        await interaction.response.send_modal(Questionnaire(mode, self.classname))

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
    async def add_basic(self,interaction:discord.Interaction):
        """
        授業基本設定
        """
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            embed = discord.Embed(color=0x2ecc71,title="基本設定")
            await interaction.response.send_message(embed=embed, view=DiscordButtonModel(classname))
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。")


    @app_commands.command()
    async def edit_schedule(self,interaction:discord.Interaction,target_date:str,period:int,value:str):
        """
        授業指定変更
        """
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
    async def user_add(self,interaction:discord.Interaction,classname:str):
        """ユーザー情報追加"""
        if not await self.user_info.check_user(interaction.user.id):
            await self.user_info.add_user(interaction.user.id,classname)
            await interaction.response.send_message("Ok")
        else:
            await interaction.response.send_message("既に追加済みです")

    
    @app_commands.command()
    async def target_check(self,interaction:discord.Interaction,date:str):
        """特定日の授業確認"""
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

    @app_commands.command()
    async def homework_add(self,interaction:discord.Interaction):
        """宿題の追加"""
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            await interaction.response.send_modal(HomeworkAdd(classname))

    @app_commands.command()
    async def homework_view(self,interaction:discord.Interaction):
        """宿題確認"""
        classname = await self.user_info.check_user(interaction.user.id)
        embed = discord.Embed(color=0x2ecc71,title=f"課題状況")
        if classname:  
            upcoming_submissions = await self.submission_manager.get_upcoming_submissions(classname)
            for deadline, assignments in upcoming_submissions.items():
                remaining_days = await self.submission_manager.count_remaining_days(deadline)
                ass = ""
                for txt  in assignments:
                    ass += txt
                    ass += "\n" 
                    
                embed.add_field(name=f"{deadline} 残り:{remaining_days}日",value=f"```{ass}```\n\n",inline=False)
                
            await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def help(self,interaction:discord.Interaction):
        """コマンドのhelp"""
        embed = discord.Embed(color=0x2ecc71,title=f"helpコマンド")
        embed.add_field(name="`/user_add [classname]`",value="```classnameは各自のクラス名 1M 1S 1E 1Cなど共通のものを使用すること (半角)```",inline=False)
        embed.add_field(name="`/add_basic`",value="```毎週の授業の基本設定```",inline=False)
        embed.add_field(name="`/edit_schedule [target_date] [period] [value]`",value="```target_date:指定日 (例2023-12-12) 指定した記述方式以外を使用しないこと(半角)\nperiod:何限目(整数)\nvalue:教科名```",inline=False)
        embed.add_field(name="`/target_check [target_date]`",value="```target_date:指定日 (例2023-12-12) 指定した記述方式以外を使用しないこと(半角)```",inline=False)
        embed.add_field(name="`/homework_add`",value="```宿題追加```",inline=False)
        embed.add_field(name="`/homework_view`",value="```宿題確認```",inline=False)
        embed.add_field(name="このBotについて",value="このBotはkazuma1112 M2303によって無償開発されています。\n開発支援金はこちらまで\nPayPay ID:kazuma11112\nKyash:ID kazuma1112\n開発費として使用します。\n開発支援-サーバー提供 [S-Server Developers](https://sdev.aknet.tech/)",inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(schedule_class(bot))
    print("[SystemLog] スケジュール Cog：ロード完了")