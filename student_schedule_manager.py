import json
from datetime import datetime, timedelta
import discord
from discord_schedule_system_class import DiscordButtonModel
from schedule_specification import Discord_Selevt_View,WeekDatesCalculator
from homework_class import Homework_view


class ClassScheduleManager:
    def __init__(self, filename='class_data.json'):
        self.filename = filename
        self.data = self.load_data()

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"classes": {}}

    async def add_class_schedule(self, class_name, schedule):
        self.data = self.load_data()
        self.data["classes"][class_name] = schedule
        self.save_data()
        return True

    async def update_class_schedule(self, class_name, date, updated_schedule):
        self.data = self.load_data()
        if class_name in self.data["classes"]:
            # 日にちごとのスケジュールを更新する
            if date in self.data["classes"][class_name]:
                self.data["classes"][class_name][date].update(updated_schedule)
            else:
                self.data["classes"][class_name][date] = updated_schedule
            self.save_data()
            return True
        else:
            return False  # 指定されたクラスが存在しない場合

    async def view_class_schedule(self, class_name, date):
        self.data = self.load_data()
        if class_name in self.data["classes"]:
            # 日にちに対応するスケジュールを取得する
            if date in self.data["classes"][class_name]:
                if self.data["classes"][class_name][date]:
                    return self.data["classes"][class_name][date]
                else:
                    day_of_week = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                    return self.data["classes"][class_name].get("Basic", {}).get(day_of_week)
            else:       
                day_of_week = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                return self.data["classes"][class_name].get("Basic", {}).get(day_of_week)

    async def edit_class_schedule(self, class_name, date, edited_schedule):
        self.data = self.load_data()
        if class_name in self.data["classes"]:
            self.data["classes"][class_name][date] = edited_schedule
            self.save_data()
            return True
        else:
            return False  # 指定されたクラスが存在しない場合

class SubmissionManager:
    def __init__(self, filename='submission_data.json'):
        self.filename = filename
        self.data = self.load_data()

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"submissions": {}}

    async def add_submission(self, class_name, deadline, assignments):
        self.data = self.load_data()
        if class_name not in self.data["submissions"]:
            self.data["submissions"][class_name] = {}
        self.data["submissions"][class_name][deadline] = assignments
        self.save_data()

    # async def view_submission(self, class_name, deadline):
    #     if class_name in self.data["submissions"]:
    #         if deadline in self.data["submissions"][class_name]:
    #             return self.data["submissions"][class_name][deadline]
    #     return None

    # async def edit_submission(self, class_name, deadline, updated_assignments):
    #     if class_name in self.data["submissions"] and deadline in self.data["submissions"][class_name]:
    #         self.data["submissions"][class_name][deadline] = updated_assignments
    #         self.save_data()
    #         return True
    #     return False

    async def get_upcoming_submissions(self, class_name):
        self.data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming_submissions = {}
        if class_name in self.data["submissions"]:
            for deadline, assignments in self.data["submissions"][class_name].items():
                if deadline >= today:
                    upcoming_submissions[deadline] = assignments
        return upcoming_submissions

    async def count_remaining_days(self, deadline):
        self.data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        remaining_days = (datetime.strptime(deadline, '%Y-%m-%d') - datetime.strptime(today, '%Y-%m-%d')).days
        return remaining_days
    
class ClassuserSystem:
    def __init__(self,filename='user_data.json'):
        self.filename = filename
        self.data = self.load_data()

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"users": {}}
    
    async def check_user(self, id):
        self.data = self.load_data()
        user_id = int(id)
        if str(user_id) in self.data["users"]:
            return list(self.data["users"][str(user_id)])
        else:
            return False

        
    async def add_user(self,id,classname):
        self.data = self.load_data()
        id = str(id)
        if id in self.data["users"]:
            for name in self.data["users"][id]:
                if name == classname:
                    return False
            classname_list:list = self.data["users"][id]
            classname_list.append(classname)
        else:
            self.data["users"][id] = classname
        self.save_data()
        return True

    async def del_user_class(self,id,classname):
        self.data = self.load_data()
        if id in self.data["users"]:
            for name in self.data["users"]:
                if name == classname:
                    classname_list:list = self.data["users"][id]
                    classname_list.pop(classname)
                    return True
                else:
                    return False
        else:
            return False
    async def del_user(self,id):
        self.data = self.load_data()
        if id in self.data["users"]:
            self.data.pop(id)
            self.save_data()
            return True
        else:
            return False
    class user_data_select(discord.ui.Select):
        def __init__(self, lists: list,command_name):
            self.command_name = command_name
            OPS = [discord.SelectOption(label=k, description="第何周かを選択してください") for k in lists]
            super().__init__(placeholder="第何周かを指定してください", min_values=1, max_values=1, options=OPS)
        async def callback(self, interaction: discord.Interaction):
            classname = self.values[0]
            num = await WeekDatesCalculator.get_number_of_weeks()
            if self.command_name == "add_basic":
                embed = discord.Embed(color=0x2ecc71,title="基本設定")
                await interaction.response.edit_message(embed=embed, view=DiscordButtonModel(classname))
            elif self.command_name == "edit_schedule":
                await interaction.response.edit_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"edit_schedule",classname))#Base
            elif self.command_name == "target_check":
                await interaction.response.edit_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"target_check",classname))
            elif self.command_name == "homework_add":
                await interaction.response.edit_message("第何周かを選択してください",view=Discord_Selevt_View(num,0,"homework_add",classname),ephemeral=True)
            elif self.command_name == "homework_view":
                embed = await Homework_view.make_embed(classname)
                await interaction.response.edit_message(embed=embed,ephemeral=True)
            elif self.command_name == "user_classname_del":
                await ClassuserSystem.del_user_class(interaction.user.id,classname)
                await interaction.response.edit_message("OK")
    class discord_user_select_View(discord.ui.View):
        def __init__(self, lists,command_name):
            super().__init__()
            self.add_item(ClassuserSystem.user_data_select(lists),command_name)