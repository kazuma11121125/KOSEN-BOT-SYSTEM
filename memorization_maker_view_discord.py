import discord
from discord import ui
import memorization_maker
from discord import app_commands
from discord.ext import commands

class Maker_button(discord.ui.SelectMenu):
    def __init__(self,selectlist,title,question):
        self.memorizationmaker = memorization_maker.MemorizationSystem()
        self.title = title  
        self.question = question
        super().__init__(placeholder="選択してください。", min_values=1, max_values=1, options=[discord.SelectOption(label=selectlist[i]) for i in range(len(selectlist))])

    async def callback(self, interaction: discord.Interaction):
        answer = self.values[0]
        result = await self.memorizationmaker.check_answer(interaction.user.id,self.title,self.question,answer)
        if result:
            await self.memorizationmaker.edit_user_status(interaction.user.id,self.title,0,1)

class Maker_Answer(ui.view):
    def __init__(self,title,question):
        super().__init__()
        self.title = title
        self.question = question
        input = ui.TextInput(label=question,style=discord.TextStyle.short) 
        self.add_item(input)
    
    async def on_submit(self,interaction:discord.Interaction):
        self.memorizationmaker = memorization_maker.MemorizationSystem()
        answer = self.items[0].value
        result = await self.memorizationmaker.check_answer(interaction.user.id,self.title,self.question,answer)
        if result:
            await self.memorizationmaker.edit_user_status(interaction.user.id,self.title,0,1)


class Memorization_question_Select(discord.ui.SelectMenu):
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
        memorization_play_main = Memorization_play_main(title, lists, interaction)
        await memorization_play_main.main_start(interaction)

class Memorization_play_main:
    """
    Represents a class for playing the memorization game.

    Attributes:
        title (str): The title of the game.
        lists (dict): The lists of content for the game.
        interaction (discord.Interaction): The interaction object for Discord.

    Methods:
        main_start(interaction: discord.Interaction): Starts the main process of the game.
    """

    def __init__(self, title, lists, interaction: discord.Interaction):
        self.title = title
        self.lists = lists
        self.memorizationmaker = memorization_maker.MemorizationSystem()

    async def main_start(self, interaction: discord.Interaction):
        """
        Starts the main process of the game.

        Args:
            interaction (discord.Interaction): The interaction object for Discord.
        """
        await self.memorizationmaker.add_user_status(interaction.user.id, self.title)
        for _ in range(len(self.lists["content"])):
            mode = self.lists["mode"]
            if mode == 0:
                view = Maker_Answer(self.title, self.lists["content"])
            elif mode == 1:
                view = Maker_button(self.lists["select"], self.title, self.lists["content"])

            await interaction.response.edit_message("問題", view=view)

class Maker_comannds_Cog(commands.Cog):
    """コグクラス: メモリゼーションメーカーのコマンドを管理するクラス"""
    def __init__(self,bot):
        self.bot = bot
        self.memorizationmaker = memorization_maker.MemorizationSystem()

    @app_commands.command()
    async def memorization_maker_view(self,interaction:discord.Interaction):
        """問題を表示するコマンド"""
        title = await self.memorizationmaker.get_mission_title(interaction.user.id)
        await interaction.response.send_message("問題を選択してください",view=Memorization_question_Select(title,"view"),ephemeral=True)

async def setup(bot):
    await bot.add_cog(Maker_comannds_Cog(bot))
    print("[SystemLog] Maker_comannds_Cog：ロード完了")