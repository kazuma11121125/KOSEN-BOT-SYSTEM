import calendar
from datetime import datetime, timedelta
import discord
from student_schedule_manager import ClassScheduleManager
from discord_schedule_system_class import ed_class
from homework_class import HomeworkAdd

class WeekDatesCalculator:
    """
    This class provides methods to calculate week dates based on the current year and month.
    """

    async def get_current_year_and_month(self):
        """
        Get the current year and month.

        Returns:
            list: A list containing the current year and month.
        """
        current_date = datetime.now()
        year = " ".join(f"{current_date.year:02}")
        month = " ".join(f"{current_date.month:02}")
        datas = [year, month]
        return datas

    async def get_week_dates(self, week_number):
        """
        Get the dates of a specific week in the current month.

        Args:
            week_number (int): The week number.

        Returns:
            list: A list of dates in the specified week.
        """
        current_date = datetime.now()
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        week_dates = []

        for week in cal:
            if week[0] != 0 and week_number == calendar.monthcalendar(current_date.year, current_date.month).index(week):
                week_dates.extend(week)
                break

        return [day for day in week_dates if day != 0]  # 週のlist

    @staticmethod
    async def get_number_of_weeks():
        """
        Get the number of weeks in the current month.

        Returns:
            int: The number of weeks.
        """
        current_date = datetime.now()
        cal = calendar.monthcalendar(current_date.year, current_date.month)
        return len(cal) - 1

class Discord_Select_Menu_weeks(discord.ui.Select):
    """
    A custom Discord select menu for selecting the week number.

    Args:
        num (int): The total number of weeks to display as options.
        comannd_name (str): The name of the command.
        classname (str): The name of the class.

    Attributes:
        comannd_name (str): The name of the command.
        classname (str): The name of the class.

    """

    def __init__(self, num, comannd_name, classname):
        self.comannd_name = comannd_name
        self.classname = classname
        OPS = [discord.SelectOption(label=f"{k+1}", description="第何周かを選択してください") for k in range(num)]
        super().__init__(placeholder="第何周かを指定してください", min_values=1, max_values=1, options=OPS)

    async def callback(self, interaction: discord.Interaction):
        self.n = self.values[0]
        n_int = int(self.n)
        lists = await WeekDatesCalculator().get_week_dates(n_int)  # インスタンスを作成してメソッドを呼び出す
        await interaction.response.edit_message(content="日付を選択してください", view=Discord_Selevt_View(lists, 1, self.comannd_name, self.classname))

class Discord_Select_Menu_days(discord.ui.Select):
    """
    A custom Discord select menu for selecting dates.

    Args:
        lists (list): The list of dates to be displayed as options.
        comannd_name (str): The name of the command.
        classname (str): The name of the class.

    Attributes:
        comannd_name (str): The name of the command.
        classname (str): The name of the class.
        num (str): The selected date.

    Methods:
        callback(interaction): The callback method called when a date is selected.

    """

    def __init__(self, lists, comannd_name, classname):
        self.comannd_name = comannd_name
        self.classname = classname
        OPS = [discord.SelectOption(label=k, description="日付を選択してください") for k in lists]
        super().__init__(placeholder="日付を選択してください", min_values=1, max_values=1, options=OPS)

    async def callback(self, interaction: discord.Interaction):
        self.num = self.values[0]
        lists = await WeekDatesCalculator().get_current_year_and_month()  # インスタンスを作成してメソッドを呼び出す
        format_string = '%Y %m %d %H %M'
        year = str(lists[0])
        year = year.replace(" ", "")
        month = str(lists[1])
        month = month.replace(" ", "")
        days = str(self.num)
        y_m_d = f"{year}-{month}-{days}"
        await main_Class_days.change_return(self.comannd_name, y_m_d, interaction, self.classname)

class Discord_Selevt_View(discord.ui.View):
    """
    A custom view class for Discord selection menus.

    Args:
        datas (list): The data to be displayed in the selection menu.
        mode (int): The mode of the view. 0 for weeks, 1 for days.
        comannd_name (str): The name of the command.
        classname (str): The name of the class.

    Attributes:
        datas (list): The data to be displayed in the selection menu.
        mode (int): The mode of the view. 0 for weeks, 1 for days.
        comannd_name (str): The name of the command.
        classname (str): The name of the class.
    """

    def __init__(self, datas, mode, comannd_name, classname):
        super().__init__()
        if mode == 0:
            self.add_item(Discord_Select_Menu_weeks(datas, comannd_name, classname))  # 第何周あるかの数字
        else:
            self.add_item(Discord_Select_Menu_days(datas, comannd_name, classname))  # 日付 list

class main_Class_days:
    """
    A class that handles various operations related to class schedules and homework.

    Methods:
    - change_return: Handles different command names and performs corresponding actions.
    """
    @staticmethod
    async def change_return(comannd_name, y_m_d, interaction: discord.Interaction, classname):
        if comannd_name == "edit_schedule":
            await interaction.response.send_modal(ed_class(classname, y_m_d))

        elif comannd_name == "target_check":
            schedule_manager = ClassScheduleManager()
            result = await schedule_manager.view_class_schedule(classname, y_m_d)
            cont = 1
            embed = discord.Embed(color=0x2ecc71, title=f"{y_m_d} 講義日程")
            for i in result:
                embed.add_field(name=f"{cont}限目", value=i, inline=False)
                cont = cont + 1
            await interaction.response.edit_message(embed=embed)

        elif comannd_name == "homework_add":
            await interaction.response.send_modal(HomeworkAdd(classname, y_m_d))
