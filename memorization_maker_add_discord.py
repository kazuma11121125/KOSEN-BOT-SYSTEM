import discord
from discord import ui
import memorization_maker
from discord import app_commands
from discord.ext import commands

class Memorization_Add_Title(ui.Modal, title="タイトル追加"):
    """
    A class representing a view for adding a title in the Memorization Maker Discord bot system.
    """

    def __init__(self):
        super().__init__()
        self.title_input = ui.TextInput(label="タイトル", style=discord.TextStyle.short)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Event handler for when the submit button is clicked.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the view.

        Returns:
        - None
        """
        title = str(self.title_input.value)
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:4", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=Memorization_Add_Discord_Button(title))

class Memorization_Add_Discord_Ui(ui.Modal,title="問題追加"):
    """
    A class representing the user interface for adding a memorization mission in a Discord bot.

    Attributes:
        title (str): The title of the memorization mission.
        inputs (list): A list of ui.TextInput objects representing the input fields for the question and answer.

    Methods:
        __init__(self, title): Initializes the Memorization_Add_Discord_Ui object.
        on_submit(self, interaction): Handles the event when the user submits the form.

    """

    def __init__(self, titles):
        super().__init__()
        self.title = titles 
        self.inputs =[
            ui.TextInput(label="問題",style=discord.TextStyle.short),
            ui.TextInput(label="答え",style=discord.TextStyle.short)
        
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the event when the user submits the form.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the bot.

        Returns:
            None

        """
        question, answer = [str(input_item) for input_item in self.inputs]
        memorization = memorization_maker.MemorizationSystem()
        await memorization.add_mission(interaction.user.id, self.title, 0, question, answer)

class Memorization_Add_Discord_Ui_Select_Edit_Count(discord.ui.Select):
    """
    A custom select menu for editing the count of selected items in the Memorization Add Discord UI.

    Args:
        title (str): The title of the select menu.

    Attributes:
        title (str): The title of the select menu.

    Methods:
        callback(interaction: discord.Interaction) -> None: The callback method that is called when the select menu is interacted with.

    """

    def __init__(self, title):
        self.title = title
        super().__init__(placeholder="選択数を選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 9)])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method that is called when the select menu is interacted with.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None

        """
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:{int(self.values[0])}", color=0x00ff00, view=Memorization_Add_Discord_Button(self.title))
        await interaction.response.edit_message(embed=embed, view=Memorization_Add_Discord_Ui_Select(self.title, int(self.values[0])))

class Memorization_Add_Discord_Ui_Select_Edit_Count_View(discord.ui.View):
    def __init__(self,title):
        super().__init__()
        self.add_item(Memorization_Add_Discord_Ui_Select_Edit_Count(title))

class Memorization_Add_Discord_Ui_Select(ui.Modal,title="問題追加"):
    """
    A class representing a user interface for adding a memorization mission with multiple choice options in a Discord bot.

    Attributes:
        title (str): The title of the memorization mission.
        select_count (int): The number of multiple choice options.

    Methods:
        __init__(self, title, select_count): Initializes the Memorization_Add_Discord_Ui_Select object.
        on_submit(self, interaction): Handles the submission of the user interface form.
    """

    def __init__(self, title, select_count):
        super().__init__()
        self.title = title
        self.inputs = [
            ui.TextInput(label="問題", style=discord.TextStyle.short),
        ]
        
        for _ in range(select_count):
            self.inputs.append(ui.TextInput(label="選択肢", style=discord.TextStyle.short))
        
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of the user interface form.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the bot.

        Returns:
            None
        """
        question = str(self.inputs[0])  # 最初の入力は問題です
        selects = [str(input_item) for input_item in self.inputs[1:]]  # 残りは選択肢です

        memorization = memorization_maker.MemorizationSystem()
        await memorization.add_mission(interaction.user.id, self.title, 1, question, selects)

    
class Memorization_question_Discord_Select(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """
    def __init__(self, lists,mode):
        """
        Initializes the Memorization_question_Discord_Select object.
        """
        self.lists = lists
        self.mode = mode
        super().__init__(placeholder="タイトルを選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=i) for i in lists])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.
        """
        memorization = memorization_maker.MemorizationSystem()
        title = self.values[0]
        lists: list = await memorization.get_mission(interaction.user.id, title)
        if self.mode == "delete":
            await interaction.response.send_message("問題を選択してください", ephemeral=True, view=Memorization_delete_Discord_Select(lists, title))
        elif self.mode == "edit":
            await interaction.response.send_message("問題を選択してください", ephemeral=True, view=Memorization_Edit_Discord_Select_View(lists, title))

class Memorization_question_Discord_Select_View(discord.ui.View):
    def __init__(self,lists,mode):
        super().__init__()
        self.add_item(Memorization_question_Discord_Select(lists,mode))

class Memorization_delete_Discord_Select(discord.ui.Select):
    """
    A custom select menu for deleting a memorization mission in Discord.

    Attributes:
    - lists (list): The list of options for the select menu.
    - title (str): The title of the mission to be deleted.

    Methods:
    - callback(interaction): The callback method called when an option is selected.
    """

    def __init__(self, lists, title):
        """
        Initializes the Memorization_delete_Discord_Select object.

        Parameters:
        - lists (list): The list of options for the select menu.
        - title (str): The title of the mission to be deleted.
        """
        self.title = title
        self.lists = lists
        super().__init__(placeholder="問題を選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.
        """
        selected_index = int(self.values[0])
        selected_question = self.lists[selected_index]["question"]
        
        memorization = memorization_maker.MemorizationSystem()
        await memorization.del_mission(interaction.user.id, self.title, selected_question)
        embed = discord.Embed(title="問題追加", color=0x00ff00, view=Memorization_Add_Discord_Button(self.title))
        await interaction.response.edit_message(embed=embed, view=Memorization_Add_Discord_Button(self.title))

class Memorization_delete_Discord_Select_View(discord.ui.View):
    def __init__(self,lists,title):
        super().__init__()
        self.add_item(Memorization_delete_Discord_Select(lists,title))

class Memorization_Edit_Discord_Select(discord.ui.Select):
    """
    A custom select menu for selecting a question in the Memorization Edit Discord UI.

    Attributes:
    - lists (list): The list of questions to be displayed in the select menu.
    - title (str): The title of the select menu.

    Methods:
    - callback(interaction: discord.Interaction): The callback method that is called when a selection is made.
    """

    def __init__(self, lists, title):
        """
        Initializes the Memorization_Edit_Discord_Select object.

        Parameters:
        - lists (list): The list of questions to be displayed in the select menu.
        - title (str): The title of the select menu.
        """
        self.title = title
        self.lists = lists
        super().__init__(placeholder="問題を選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=str(i), value="選択してください") for i in lists])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method that is called when a selection is made.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.
        """
        selected_index = int(self.values[0])
        selected_question = self.lists[selected_index]["question"]
        if selected_question["mode"] == 0:
            await interaction.response.send_modal(Memorization_Edit_Discord_Ui_Mode_0(self.title))
        else:
            await interaction.response.send_modal(Memorization_Edit_Discord_Ui_Mode_1(self.title, len(selected_question["select"])))

class Memorization_Edit_Discord_Select_View(discord.ui.View):
    """
    A custom view class for the Memorization_Edit_Discord_Select select menu.

    Attributes:
    - lists (list): The list of questions to be displayed in the select menu.
    - title (str): The title of the select menu.

    Methods:
    - __init__(self, lists, title): Initializes the Memorization_Edit_Discord_Select_View object.
    """

    def __init__(self, lists, title):
        """
        Initializes the Memorization_Edit_Discord_Select_View object.

        Parameters:
        - lists (list): The list of questions to be displayed in the select menu.
        - title (str): The title of the select menu.
        """
        super().__init__()
        self.add_item(Memorization_Edit_Discord_Select(lists, title))

class Memorization_Edit_Discord_Ui_Mode_0(ui.Modal,title="問題編集"):
    """
    Represents a user interface mode for editing memorization data in a Discord bot.
    """

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.inputs = [
            ui.TextInput(label="問題", style=discord.TextStyle.short),
            ui.TextInput(label="答え", style=discord.TextStyle.short)
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        question, answer = [str(input_item) for input_item in self.inputs]
        memorization = memorization_maker.MemorizationSystem()
        await memorization.edit_misson(interaction.user.id, self.title, 0, question, answer)
        await interaction.response.send_message("編集完了", ephemeral=True)

class Memorization_Edit_Discord_Ui_Mode_1(ui.Modal,title="問題編集"):
    """
    A class representing a user interface for adding a memorization mission with multiple choice options in a Discord bot.

    Attributes:
        title (str): The title of the memorization mission.
        select_count (int): The number of multiple choice options.

    Methods:
        __init__(self, title, select_count): Initializes the Memorization_Add_Discord_Ui_Select object.
        on_submit(self, interaction): Handles the submission of the user interface form.
    """

    def __init__(self, title, select_count):
        super().__init__()
        self.title = title
        self.inputs = [
            ui.TextInput(label="問題", style=discord.TextStyle.short),
        ]
        
        for _ in range(select_count):
            self.inputs.append(ui.TextInput(label="選択肢", style=discord.TextStyle.short))
        
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        question, answer = [str(input_item) for input_item in self.inputs]
        memorization = memorization_maker.MemorizationSystem()
        await memorization.edit_misson(interaction.user.id, self.title, 0, question, answer)
        await interaction.response.send_message("編集完了",ephemeral=True)

class Memorization_Add_Discord_Button(discord.ui.View):
    """
    Discord UI button for adding memorization questions.

    Args:
        title (str): The title of the memorization question.
        base_count (int, optional): The base count for the question. Defaults to 4.
    """
    def __init__(self,title,base_count=4):
        super().__init__()
        self.base_count = base_count
        self.title = title
    
    async def swithcing(self,interaction:discord.Interaction,button,mode):
        if mode == "add":
            await interaction.response.send_modal(Memorization_Add_Discord_Ui(self.title))
        elif mode == "select_add":
            await interaction.response.send_modal(Memorization_Add_Discord_Ui_Select(self.title, self.base_count))
        elif mode == "count":
            await interaction.response.edit_message("選択数を選択してください",view=Memorization_Add_Discord_Ui_Select_Edit_Count_View(self.title))
        elif mode == "delete":
            memorization = memorization_maker.MemorizationSystem()
            lists:list = await memorization.get_mission(interaction.user.id,self.title)
            await interaction.response.send_message("削除する問題を選択してください",view=Memorization_delete_Discord_Select_View(lists,self.title),ephemeral=True)
        elif mode == "edit":
            memorization = memorization_maker.MemorizationSystem()
            lists = await memorization.get_mission(interaction.user.id,self.title)
            await interaction.response.send_message("編集する問題を選択してください",view=Memorization_Edit_Discord_Select_View(lists,self.title),ephemeral=True)
        elif mode == "close":
            await interaction.response.edit_message("終了")
            
    @discord.ui.button(label="問題を追加", style=discord.ButtonStyle.blurple)
    async def add(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"add")
        
    @discord.ui.button(label="選択問題を追加", style=discord.ButtonStyle.green)
    async def select_add(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"select_add")   
             
    @discord.ui.button(label="選択数変更", style=discord.ButtonStyle.gray)
    async def count(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"count")
        
    @discord.ui.button(label="問題を削除", style=discord.ButtonStyle.red)
    async def delete(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"delete")

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.red)
    async def edit(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"edit")
    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self,interaction:discord.Interaction,button:discord.ui.Button):
        await self.swithcing(interaction,button,"close")
class Memorization_maker_main_Cog(commands.Cog):
    def __init__(self, bot):
        """
        Initializes an instance of the class.

        Parameters:
        - bot: The Discord bot object.

        Returns:
        - None
        """
        self.bot = bot
        self.memorization = memorization_maker.MemorizationSystem()

    @app_commands.command()
    async def memorization_add(self, interaction: discord.Interaction):
        """
        メモリゼーションを追加するコマンドです。

        Parameters:
            interaction (discord.Interaction): Discordのインタラクションオブジェクト

        Returns:
            None
        """
        await interaction.response.send_modal(Memorization_Add_Title())

    @app_commands.command()
    async def memorization_delete(self, interaction: discord.Interaction):
        """
        Deletes a memorization question.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the command.

        Returns:
        None
        """
        lists = await self.memorization.get_mission_title(interaction.user.id)
        await interaction.response.send_message("削除する問題を選択してください", view=Memorization_question_Discord_Select_View(lists, "delete"), ephemeral=True)

    @app_commands.command()
    async def memorization_edit(self, interaction: discord.Interaction):
        """
        メモリゼーションの問題を編集するコマンドです。

        Parameters:
            interaction (discord.Interaction): Discordのインタラクションオブジェクト

        Returns:
            None
        """
        lists = await self.memorization.get_mission_title(interaction.user.id)
        await interaction.response.send_message("編集する問題を選択してください", view=Memorization_question_Discord_Select(lists, "edit"), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Memorization_maker_main_Cog(bot))
    print("[SystemLog] memorization_maker_add_discord loaded")