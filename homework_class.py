import discord
from discord import ui
from student_schedule_manager import SubmissionManager

class HomeworkAdd(ui.Modal, title="課題追加"):
    """
    A class representing a modal for adding homework.

    Args:
        classname (str): The name of the class.
        y_m_d (str): The date in the format "YYYY-MM-DD".

    Attributes:
        classname (str): The name of the class.
        y_m_d (str): The date in the format "YYYY-MM-DD".
        submission_manager (SubmissionManager): An instance of the SubmissionManager class.
        name (ui.TextInput): A text input field for entering the homework details.

    Methods:
        on_submit: A method that is called when the form is submitted.

    """

    def __init__(self, classname, y_m_d):
        super().__init__()
        self.classname = classname
        self.y_m_d = y_m_d
        self.submission_manager = SubmissionManager()
        self.name = ui.TextInput(label="詳細", style=discord.TextStyle.paragraph)
        self.add_item(self.name)

    async def on_submit(self, interaction: discord.Interaction):
        """
        A method that is called when the form is submitted.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the form.

        """
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

        await interaction.response.send_message("add homework ok", ephemeral=True)
        
class Homework_view:
    """
    A class representing a homework view.

    Methods:
    - make_embed(classname): Create an embed object with upcoming homework assignments for a given class.
    """

    @staticmethod
    async def make_embed(classname):
        """
        Create an embed object with upcoming homework assignments for a given class.

        Parameters:
        - classname (str): The name of the class.

        Returns:
        - embed (discord.Embed): The embed object containing the homework assignments.
        """
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