import json
from datetime import datetime, timedelta

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
            return self.data["users"][str(user_id)]
        else:
            return False

        
    async def add_user(self,id,classname):
        self.data = self.load_data()
        if not id in self.data["users"]:
            self.data["users"][id] = classname
            self.save_data()
            return True
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
    """
    A class that manages submissions for different classes and deadlines.

    Attributes:
        filename (str): The name of the file to save the submission data.
        data (dict): The dictionary that stores the submission data.

    Methods:
        save_data(): Saves the submission data to a file.
        load_data(): Loads the submission data from a file.
        add_submission(class_name, deadline, assignments): Adds a new submission for a class and deadline.
        get_upcoming_submissions(class_name): Retrieves the upcoming submissions for a class.
        count_remaining_days(deadline): Counts the remaining days until a deadline.
    """

    def __init__(self, filename='submission_data.json'):
        self.filename = filename
        self.data = self.load_data()

    def save_data(self):
        """
        Saves the submission data to a file.
        """
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def load_data(self):
        """
        Loads the submission data from a file.
        If the file is not found, returns an empty dictionary.

        Returns:
            dict: The loaded submission data.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"submissions": {}}

    async def add_submission(self, class_name, deadline, assignments):
        """
        Adds a new submission for a class and deadline.

        Args:
            class_name (str): The name of the class.
            deadline (str): The deadline for the submission in the format 'YYYY-MM-DD'.
            assignments (str): The assignments for the submission.

        """
        self.data = self.load_data()
        if class_name not in self.data["submissions"]:
            self.data["submissions"][class_name] = {}
        self.data["submissions"][class_name][deadline] = assignments
        self.save_data()

    async def get_upcoming_submissions(self, class_name):
        """
        Retrieves the upcoming submissions for a class.

        Args:
            class_name (str): The name of the class.

        Returns:
            dict: A dictionary containing the upcoming submissions for the class, where the keys are the deadlines and the values are the assignments.
        """
        self.data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming_submissions = {}
        if class_name in self.data["submissions"]:
            for deadline, assignments in self.data["submissions"][class_name].items():
                if deadline >= today:
                    upcoming_submissions[deadline] = assignments
        return upcoming_submissions

    async def count_remaining_days(self, deadline):
        """
        Counts the remaining days until a deadline.

        Args:
            deadline (str): The deadline in the format 'YYYY-MM-DD'.

        Returns:
            int: The number of remaining days until the deadline.
        """
        self.data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        remaining_days = (datetime.strptime(deadline, '%Y-%m-%d') - datetime.strptime(today, '%Y-%m-%d')).days
        return remaining_days