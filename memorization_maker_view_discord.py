import discord
from discord import ui
import memorization_maker
from discord import app_commands
from discord.ext import commands

class MakerSelect(discord.ui.Select):
    def __init__(self,selectlist,title,question,count):
        """
        Initializes a MakerSelect object.

        Args:
        - selectlist (list): A list of options for the select dropdown.
        - title (str): The title of the question.
        - question (str): The question to be displayed.
        - count (int): The count of the question.

        Returns:
        - None
        """
        self.memorizationmaker = memorization_maker.MemorizationSystem()
        self.title = title  
        self.question = question
        self.count = count
        super().__init__(placeholder="選択してください。", min_values=1, max_values=1, options=[discord.SelectOption(label=selectlist[i]) for i in range(len(selectlist))])

    async def callback(self, interaction: discord.Interaction):
        """
        Callback function for the select dropdown.

        Args:
        - interaction (discord.Interaction): The interaction object.

        Returns:
        - None
        """
        answer = self.values[0]
        result = await self.memorizationmaker.check_answer(interaction.user.id,self.title,self.question,answer,1)
        if result:
            await self.memorizationmaker.edit_user_status(interaction.user.id,self.title,0,1)
            ch = "正解"
        else:
            ch = "不正解"
        embed = discord.Embed(title="回答結果",color=0x00ff00)
        embed.add_field(name="あなたの回答",value=f"{answer}",inline=False)
        embed.add_field(name="正誤",value=f"あなたの回答は{ch}です",inline=False)
        await interaction.response.edit_message(embed=embed,view=MakerAmwerButtonContenu(self.title,self.question,self.count))

    
class MakerSelectView(discord.ui.View):
    def __init__(self, lists, title, question, count):
        """
        Initializes a MakerSelectView object.

        Args:
            lists (list): The list of options for selection.
            title (str): The title of the view.
            question (str): The question to be displayed.
            count (int): The count of options to be displayed.

        Returns:
            None
        """
        super().__init__()
        self.add_item(MakerSelect(lists, title, question, count))
class MakerSelectView(discord.ui.View):
    def __init__(self,lists,title,question,count):
        super().__init__()
        self.add_item(MakerSelect(lists,title,question,count))

class MakerAnswer(ui.Modal,title="回答"):
    """
    A class representing the modal for answering a question in the memorization maker system.

    Args:
    - title (str): The title of the modal.
    - question (str): The question to be answered.
    - counts (int): The number of counts.

    Attributes:
    - title (str): The title of the modal.
    - question (str): The question to be answered.
    - counts (int): The number of counts.
    - input (ui.TextInput): The input field for the answer.

    Methods:
    - on_submit(interaction: discord.Interaction): Handles the submission of the answer.
    """

    def __init__(self, title, question, counts):
        super().__init__()
        self.title = title
        self.question = question
        self.counts = counts
        self.input = ui.TextInput(label=question, style=discord.TextStyle.short)
        self.add_item(self.input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of the answer.

        Args:
        - interaction (discord.Interaction): The interaction object representing the user's interaction.

        Returns:
        - None
        """
        self.memorizationmaker = memorization_maker.MemorizationSystem()
        answer = str(self.input.value)
        result = await self.memorizationmaker.check_answer(interaction.user.id, self.title, self.question, answer, 0)
        if result:
            await self.memorizationmaker.edit_user_status(interaction.user.id, self.title, 0, 1)
            ch = "正解"
        else:
            ch = "不正解"
            
        embed = discord.Embed(title="回答結果", color=0x00ff00)
        embed.add_field(name="あなたの回答", value=f"{answer}", inline=False)
        embed.add_field(name="正誤", value=f"あなたの回答は{ch}です", inline=False)
        await interaction.response.edit_message(embed=embed, view=MakerAmwerButtonContenu(self.title, self.question, self.counts))

class MakerAmwerButtonContenu(discord.ui.View):
    def __init__(self, title, question, count):
        """
        コンストラクタ

        :param title: タイトル
        :param question: 質問
        :param count: カウント
        """
        self.title = title
        self.question = question
        self.count = count
        super().__init__()

    @discord.ui.button(label="次に進む", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        ボタンのコールバック関数

        :param interaction: インタラクション
        :param button: ボタン
        """
        self.count += 1
        memorization = memorization_maker.MemorizationSystem()
        lists: list = await memorization.get_mission(interaction.user.id, self.title)
        memorizationPlayMain = MemorizationPlayMain(self.title, lists, self.count, interaction)
        await memorizationPlayMain.main_start(interaction)

class MakerAnwerButton(discord.ui.View):
    """
    A custom button class for answering questions in the memorization maker view.

    Attributes:
        title (str): The title of the question.
        question (str): The content of the question.
        mode (int): The mode of the view.
        counts (int): The number of counts.
        select (Optional): The optional select parameter.

    Methods:
        callback(interaction: discord.Interaction, button: discord.ui.Button) -> None:
            The callback method for handling button interactions.
    """

    def __init__(self, title, question, mode, counts, select=None):
        super().__init__()
        self.title = title
        self.question = question
        self.mode = mode
        self.select = select
        self.counts = counts

    @discord.ui.button(label="回答する", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode == 0:
            await interaction.response.send_modal(MakerAnswer(self.title, self.question, self.counts))
        elif self.mode == 1:
            view = MakerSelectView(self.select, self.title, self.question, self.counts)
            await interaction.response.edit_message(view=view)


class MemorizationQuestionSelect(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """

    def __init__(self, lists, mode):
        """
        Initializes the Memorization_question_Discord_Select object.

        Args:
            lists (list): The list of options to be displayed in the select menu.
            mode (str): The mode of the memorization mission.

        Returns:
            None
        """
        self.lists = lists
        self.mode = mode
        super().__init__(placeholder="タイトルを選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=i) for i in lists])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None
        """
        memorization = memorization_maker.MemorizationSystem()
        title = self.values[0]
        lists: list = await memorization.get_mission(interaction.user.id, title)
        memorizationPlayMain = MemorizationPlayMain(title, lists,0,interaction)
        await memorizationPlayMain.main_start(interaction)

class MemorizationQuestionSelect_View(discord.ui.View):
    """
    A custom view class for the MemorizationQuestionSelect select menu.
    """

    def __init__(self, lists, mode):
        """
        Initializes the MemorizationQuestionSelect_View object.

        Args:
            lists (list): The list of options to be displayed in the select menu.
            mode (str): The mode of the memorization mission.

        Returns:
            None
        """
        super().__init__()
        self.add_item(MemorizationQuestionSelect(lists, mode))
        
class MemorizationPlayMain:
    """
    Represents a class for playing the memorization game.

    Attributes:
        title (str): The title of the game.
        lists (dict): The lists of content for the game.
        counts (int): The number of times the game has been played.
        interaction (discord.Interaction): The interaction object for Discord.

    Methods:
        main_start(interaction: discord.Interaction): Starts the main process of the game.
    """

    def __init__(self, title, lists,counts, interaction: discord.Interaction):
        self.title = title
        self.lists = lists
        self.counts = counts
        self.memorizationmaker = memorization_maker.MemorizationSystem()

    async def main_start(self, interaction: discord.Interaction):
        """
        Starts the main process of the game.

        Args:
            interaction (discord.Interaction): The interaction object for Discord.
        """
        if self.counts == len(self.lists):
            dicts:dict = await self.memorizationmaker.get_user_status(interaction.user.id, self.title)
            score = dicts["score"] 
            count = dicts["count"]
            embed = discord.Embed(title=f"{count}回目の挑戦終了",color=0x00ff00)
            embed.add_field(name="結果",value=f"問題: [{self.title}]のスコアは{score}点です")
            await interaction.response.send_message(embed=embed,ephemeral=True)
            return
        if self.counts == 0:
            await self.memorizationmaker.add_user_status(interaction.user.id, self.title)
            await self.memorizationmaker.edit_user_status(interaction.user.id, self.title, 1, 0)
        mode = self.lists[self.counts]["mode"]
        question = self.lists[self.counts]["question"]
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=f"{question}",inline=False)
        if mode == 0:
            view = MakerAnwerButton(self.title,question,mode,self.counts)
            await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
        elif mode == 1:
            select = self.lists[self.counts]["select"]
            view = MakerAnwerButton(self.title,question,mode,self.counts,select)
            await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
    
class MakerComanndsCog(commands.Cog):
    """コグクラス: メモリゼーションメーカーのコマンドを管理するクラス"""
    def __init__(self,bot):
        self.bot = bot
        self.memorizationmaker = memorization_maker.MemorizationSystem()

    @app_commands.command()
    async def memorization_maker_view(self,interaction:discord.Interaction):
        """問題を表示するコマンド"""
        title = await self.memorizationmaker.get_mission_title(interaction.user.id)
        embed = discord.Embed(title="問題を選択してください",color=0x00ff00)
        await interaction.response.send_message(embed=embed,view= MemorizationQuestionSelect_View(title,"view"),ephemeral=True)

async def setup(bot):
    await bot.add_cog(MakerComanndsCog(bot))
    print("[SystemLog] memorization_maker_view loaded")