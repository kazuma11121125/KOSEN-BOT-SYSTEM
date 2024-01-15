import discord
from discord import ui
from student_schedule_manager import SubmissionManager

class HomeworkAdd(ui.Modal, title="課題追加"):
    def __init__(self, classname,y_m_d):
        super().__init__()
        self.classname = classname
        self.y_m_d = y_m_d
        self.submission_manager = SubmissionManager()
        self.name = ui.TextInput(label="詳細", style=discord.TextStyle.paragraph)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        data = self.submission_manager.load_data()
        name = str(self.name)
        date = str(self.y_m_d)
        if self.classname in data["submissions"]:
            try:
                base = data["submissions"][self.classname][date]
            except KeyError:
                base = []
        else:
            # If self.classname is not present, create a new entry
            data["submissions"][self.classname] = {date: []}
            base = []

        base.append(name)
        await self.submission_manager.add_submission(self.classname, date, base)

        await interaction.response.send_message("add homework ok",ephemeral=True)
        
class Homework_view:
    
    @staticmethod
    async def make_embed(classname):
        submission_manager = SubmissionManager()
        embed = discord.Embed(color=0x2ecc71,title=f"課題状況")
        upcoming_submissions = await submission_manager.get_upcoming_submissions(classname)
        for deadline, assignments in upcoming_submissions.items():
            remaining_days = await submission_manager.count_remaining_days(deadline)
            ass = ""
            for txt  in assignments:
                ass += txt
                ass += "\n" 
                    
            embed.add_field(name=f"{deadline} 残り:{remaining_days}日",value=f"```{ass}```\n\n",inline=False)
            
        return embed