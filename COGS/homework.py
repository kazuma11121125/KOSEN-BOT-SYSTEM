import discord
from discord.ext import commands
from discord import app_commands
from student_schedule_manager import ClassuserSystem,SubmissionManager
from homework_class import Homework_view
from schedule_specification import WeekDatesCalculator,Discord_Selevt_View
class HomeworkClass(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.submission_manager = SubmissionManager()
        self.user_info = ClassuserSystem()

    @app_commands.command()
    async def homework_add(self,interaction:discord.Interaction):
        """宿題の追加"""
        classname_list = await self.user_info.check_user(interaction.user.id)
        await interaction.response.send_message("クラスを選択してください",view=self.user_info.user_data_select(classname_list,"homework_add"),ephemeral=True)

    @app_commands.command()
    async def homework_view(self,interaction:discord.Interaction):
        """宿題確認"""
        classname_list = await self.user_info.check_user(interaction.user.id)
        await interaction.response.send_message("クラスを選択してください",view=self.user_info.user_data_select(classname_list,"homework_view"),ephemeral=True)

async def setup(bot):
    await bot.add_cog(HomeworkClass(bot))
    print("[SystemLog] homework Cog：ロード完了")