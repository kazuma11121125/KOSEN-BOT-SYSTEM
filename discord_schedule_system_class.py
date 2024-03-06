import discord
from discord import ui
from student_schedule_manager import ClassScheduleManager,ClassuserSystem
from homework_class import Homework_view
class Questionnaire(ui.Modal, title="教科入力"):
    """
    A class representing a questionnaire for inputting class schedules.

    Attributes:
    - mode (str): The mode of the questionnaire.
    - class_name (str): The name of the class.
    - schedule_manager (ClassScheduleManager): An instance of the ClassScheduleManager class.
    - inputs (list): A list of TextInput objects representing the input fields for each class schedule.

    Methods:
    - __init__(self, mode, class_name): Initializes the Questionnaire object.
    - on_submit(self, interaction): Handles the submission of the questionnaire.
    """
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

        await interaction.response.send_message(embed=embed, ephemeral=True)

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
    """
    A class representing a modal for changing classes.

    Attributes:
    - classname (str): The name of the class.
    - y_m_d (str): The date of the class in the format 'YYYY-MM-DD'.
    - period (ui.TextInput): The input field for the class period.
    - value (ui.TextInput): The input field for the class name.
    """

    def __init__(self,classname,y_m_d):
        super().__init__()
        self.classname = classname
        self.y_m_d = y_m_d
        self.period = ui.TextInput(label="何限目 (整数数字のみ記入)", style=discord.TextStyle.short)
        self.value = ui.TextInput(label="授業名",style=discord.TextStyle.short)
        self.add_item(self.period)
        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        target_date = str(self.y_m_d)
        period = str(self.period)
        value = str(self.value)
        self.user_info = ClassuserSystem()
        self.schedule_manager = ClassScheduleManager()
        classname = await self.user_info.check_user(interaction.user.id)
        if classname:
            base = await self.schedule_manager.view_class_schedule(classname,target_date)
            period = int(period)
            if period < 5:
                period = period -1
                base[period] = value
                await self.schedule_manager.edit_class_schedule(classname, target_date, base)
                await interaction.response.send_message("OK",ephemeral=True)
            else:
                await interaction.response.send_message(f"ん？？？\nそんな授業数ないお{period}",ephemeral=True)
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。",ephemeral=True)
        
class DiscordButtonModel_disbord(discord.ui.View):
    """
    DiscordButtonModel_disbord is a class that represents a view for Discord buttons in a Discord bot.
    It provides functionality for handling different button interactions and switching between different modes.

    Attributes:
    - user_info: An instance of the ClassuserSystem class.
    - homework: An instance of the Homework_view class.

    Methods:
    - __init__: Initializes the DiscordButtonModel_disbord class.
    - switching: Handles the switching logic based on the button interaction and mode.
    - mon: Button handler for "基本日程設定" button.
    - change: Button handler for "授業変更適用" button.
    - class_view: Button handler for "授業確認" button.
    - homework_add: Button handler for "宿題追加" button.
    - homework_view: Button handler for "宿題確認" button.
    """
    def __init__(self):
        super().__init__(timeout=None)  # Set a longer timeout or None for no timeout
        self.user_info = ClassuserSystem()
        self.homework = Homework_view()

    async def switching(self, interaction: discord.Interaction, button, mode):
        """
        Handles the switching logic based on the button interaction and mode.

        Parameters:
        - interaction: The discord.Interaction object representing the button interaction.
        - button: The button object.
        - mode: The mode indicating the action to be performed.

        Returns:
        None
        """
        from schedule_specification import WeekDatesCalculator ,Discord_Selevt_View
        classname = await self.user_info.check_user(interaction.user.id)
        num = await WeekDatesCalculator.get_number_of_weeks()
        if classname:
            if mode == "Base":
                embed = discord.Embed(color=0x2ecc71,title="基本設定")
                await interaction.response.send_message(embed=embed, view=DiscordButtonModel(classname),ephemeral=True)
            if mode == "change":
               await interaction.response.send_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"edit_schedule",classname),ephemeral=True)#Base
            if mode == "classview":
                await interaction.response.send_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"target_check",classname),ephemeral=True)
            if mode == "homework_add":
               await interaction.response.send_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"homework_add",classname),ephemeral=True)
            if mode == "homework_view":
                embed = await self.homework.make_embed(classname)
                await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            await interaction.response.send_message("ユーザー情報がみつかりませんでした。",ephemeral=True)

    @discord.ui.button(label="基本日程設定",style=discord.ButtonStyle.blurple,custom_id="Base")
    async def mon(self, button, interaction):
        """
        Button handler for "基本日程設定" button.

        Parameters:
        - button: The button object.
        - interaction: The discord.Interaction object representing the button interaction.

        Returns:
        None
        """
        await self.switching(button, interaction, "Base")

    @discord.ui.button(label="授業変更適用",style=discord.ButtonStyle.red,custom_id="change")
    async def change(self,button,interaction):
        """
        Button handler for "授業変更適用" button.

        Parameters:
        - button: The button object.
        - interaction: The discord.Interaction object representing the button interaction.

        Returns:
        None
        """
        await self.switching(button,interaction,"change")
        
    @discord.ui.button(label="授業確認",style=discord.ButtonStyle.red,custom_id="classview")
    async def class_view(self,button,interaction):
        """
        Button handler for "授業確認" button.

        Parameters:
        - button: The button object.
        - interaction: The discord.Interaction object representing the button interaction.

        Returns:
        None
        """
        await self.switching(button,interaction,"classview")
        
    @discord.ui.button(label="宿題追加",style=discord.ButtonStyle.green,custom_id="homework_add")
    async def homework_add(self,button,interaction):
        """
        Button handler for "宿題追加" button.

        Parameters:
        - button: The button object.
        - interaction: The discord.Interaction object representing the button interaction.

        Returns:
        None
        """
        await self.switching(button,interaction,"homework_add")
        
    @discord.ui.button(label="宿題確認",style=discord.ButtonStyle.green,custom_id="homework_view")
    async def homework_view(self,button,interaction):
        """
        Button handler for "宿題確認" button.

        Parameters:
        - button: The button object.
        - interaction: The discord.Interaction object representing the button interaction.

        Returns:
        None
        """
        await self.switching(button,interaction,"homework_view")
        
