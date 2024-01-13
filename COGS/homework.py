import discord
from discord.ext import commands
from discord import app_commands
from student_schedule_manager import ClassuserSystem,SubmissionManager
from homework_class import HomeworkAdd

class HomeworkClass(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.submission_manager = SubmissionManager()
        self.user_info = ClassuserSystem()

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
                
            await interaction.response.send_message(embed=embed,ephemeral=True)    

async def setup(bot):
    await bot.add_cog(HomeworkClass(bot))
    print("[SystemLog] homework Cog：ロード完了")