import discord
from discord.ext import commands, tasks
from datetime import datetime,timedelta
from discord import app_commands
from student_schedule_manager import ClassScheduleManager,SubmissionManager,ClassuserSystem
from discord_schedule_system_class import ed_class,DiscordButtonModel,DiscordButtonModel_disbord

class schedule_class(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.schedule_manager = ClassScheduleManager()
        self.submission_manager = SubmissionManager()
        self.user_info = ClassuserSystem()
        self.send_dict = {
            "1M":[1184742396492263454],
            "1S":[1184742458781864007],
            "1C":[1184753367289974794],
            "1E":[1184753468620152922]
        }
        self.loop_start.start()
        self.check = False
    @app_commands.command()
    async def add_basic(self,interaction:discord.Interaction):
        """授業基本設定"""
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            embed = discord.Embed(color=0x2ecc71,title="基本設定")
            await interaction.response.send_message(embed=embed, view=DiscordButtonModel(classname),ephemeral=True)
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。")

    @app_commands.command()
    async def edit_schedule(self,interaction:discord.Interaction):
        """授業指定変更"""
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            await interaction.response.send_modal(ed_class(classname))
        else:
            await interaction.response.send_message("ユーザー情報が見つかりませんでした。",ephemeral=True)

    @app_commands.command()
    async def user_add(self,interaction:discord.Interaction,classname:str):
        """ユーザー情報追加"""
        if not await self.user_info.check_user(interaction.user.id):
            await self.user_info.add_user(interaction.user.id,classname)
            await interaction.response.send_message("Ok",ephemeral=True)
        else:
            await interaction.response.send_message("既に追加済みです",ephemeral=True)

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
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            await interaction.response.send_message("ユーザー情報が見つかりませんでした。",ephemeral=True)

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
        await interaction.response.send_message(embed=embed,ephemeral=True)

    @tasks.loop(seconds=15)
    async def loop_start(self):
        try:
            now = datetime.now()
            if now.strftime("%H:%M") == "16:30" and self.check == False:
                lists = ["1M","1S","1C","1E"]
                for name in lists:
                    today = datetime.now().date()
                    tomorrow = today + timedelta(days=1)
                    tomorrow = str(tomorrow)
                    result = await self.schedule_manager.view_class_schedule(name, tomorrow)
                    upcoming_submissions = await self.submission_manager.get_upcoming_submissions(name)
                    cont = 1
                    embed = discord.Embed(color=0x2ecc71,title=f"{name}スケジュール")
                    if result:
                        embed.add_field(name=f"-----明日({tomorrow}) 講義日程-----",value="",inline=False)
                        for i in result:
                            embed.add_field(name=f"{cont}限目",value=i,inline=False)
                            cont += 1
                    else:
                        embed = discord.Embed(color=0x2ecc71,title=f"{name} 講義日程未登録")
                    embed.add_field(name="-----課題状況-----",value="",inline=False)
                    if upcoming_submissions:
                        for deadline, assignments in upcoming_submissions.items():
                            remaining_days = await self.submission_manager.count_remaining_days(deadline)
                            ass = ""
                            for txt  in assignments:
                                ass += txt
                                ass += "\n" 
                                
                            embed.add_field(name=f"{deadline} 残り:{remaining_days}日",value=f"```{ass}```\n\n",inline=False)
                    else:
                        embed.add_field(name="課題情報未登録",value="",inline=False)
                    for id in self.send_dict[name]:
                        if id:   
                            await self.bot.get_channel(id).send(embed=embed)
                self.check = True
            if now.strftime("%H:%M") == "16:31":
                self.check = False
        except Exception as e:
            await self.bot.get_channel(id).send(f"An error occurred: {type(e).__name__} - {e}")        

async def setup(bot):
    await bot.add_cog(schedule_class(bot))
    print("[SystemLog] スケジュール Cog：ロード完了")