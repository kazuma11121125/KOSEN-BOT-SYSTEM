import discord
from discord import ui
from student_schedule_manager import ClassScheduleManager,ClassuserSystem

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

        await interaction.response.send_message(embed=embed,ephemeral=True)

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

class ed_class(ui.Modal,title="授業変更"):
    def __init__(self,classname):
        super().__init__()
        self.classname = classname
        self.date = ui.TextInput(label="日付設定 (2024-01-13形式で記入)", style=discord.TextStyle.short)
        self.period = ui.TextInput(label="何限目 (整数数字のみ記入)", style=discord.TextStyle.short)
        self.value = ui.TextInput(label="授業名",style=discord.TextStyle.short)
        self.add_item(self.date)
        self.add_item(self.period)
        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        target_date = str(self.date)
        period = str(self.period)
        value = str(self.value)
        self.user_info = ClassuserSystem()
        self.schedule_manager = ClassScheduleManager()
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            base = await self.schedule_manager.view_class_schedule(classname,target_date)
            if period < 5:
                period = period -1
                base[period] = value
                await self.schedule_manager.edit_class_schedule(classname, target_date, base)
                await interaction.response.send_message("OK")
            else:
                await interaction.response.send_message(f"ん？？？\nそんな授業数ないお{period}",ephemeral=True)
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。",ephemeral=True)    

class DiscordButtonModel_disbord(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set a longer timeout or None for no timeout
        self.user_info = ClassuserSystem()

    # Define a simple View that persists between bot restarts
    # In order for a view to persist between restarts it needs to meet the following conditions:
    # 1) The timeout of the View has to be set to None
    # 2) Every item in the View has to have a custom_id set
    # It is recommended that the custom_id be sufficiently unique to
    # prevent conflicts with other buttons the bot sends.
    # For this example the custom_id is prefixed with the name of the bot.
    # Note that custom_ids can only be up to 100 characters long.
    async def switching(self, interaction: discord.Interaction, button, mode):
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            if mode == "Base":
                embed = discord.Embed(color=0x2ecc71,title="基本設定")
                await interaction.response.send_message(embed=embed, view=DiscordButtonModel(classname),ephemeral=True)
            if mode == "change":
               await interaction.response.send_modal(ed_class(classname))
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。",ephemeral=True)

    @discord.ui.button(label="基本日程設定",style=discord.ButtonStyle.blurple,custom_id="Base")
    async def mon(self, button, interaction):
        await self.switching(button, interaction, "Base")

    @discord.ui.button(label="授業変更適用",style=discord.ButtonStyle.blurple,custom_id="change")
    async def change(self,button,interaction):
        await self.switching(button,interaction,"change")