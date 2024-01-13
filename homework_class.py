import discord
from discord import ui
from student_schedule_manager import SubmissionManager

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
            # If self.classname is not present, create a new entry
            data["submissions"][self.classname] = {date: []}
            base = []

        base.append(name)
        await self.submission_manager.add_submission(self.classname, date, base)

        await interaction.response.send_message("add homework ok")