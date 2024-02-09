import json

class MemorizationSystem:
    def __init__(self,filename='memorization.json'):
        self.filename = filename
        self.data = self.load_data()

    async def save_data(self):
        """
        Save the data to a file in JSON format.

        Args:
            None

        Returns:
            None
        """
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    async def load_data(self):
        """
        Loads the data from a file and returns it as a dictionary.

        If the file is not found, an empty dictionary is returned.

        Returns:
            dict: The loaded data as a dictionary.
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"memorization": {}}

    async def add_mission(self, id, title, mode, mission, answer, select=None):
        """
        Add a mission to the memorization data.

        Args:
            id (str): The ID of the memorization.
            title (str): The title of the mission.
            mode (int): The mode of the mission. 0 for normal mission, 1 for multiple-choice mission.
            mission (str): The mission question.
            answer (str): The answer to the mission.
            select (list, optional): The list of options for multiple-choice mission. Defaults to None.

        Returns:
            bool: True if the mission is added successfully, False otherwise.
        """
        self.data = await self.load_data()
        if not id in self.data["memorization"]:
            if not id in self.data["memorization"]:
                self.data["memorization"][id] = {title: {"content": []}}
            if mode == 0:
                self.data["memorization"][id][title]["content"].append({"question": mission, "mode": mode, "answer": answer})

            if mode == 1:
                self.data["memorization"][id][title]["content"].append({"question": mission, "mode": mode, "select": select, "answer": answer})
            return True
        else:
            return False

    async def del_mission(self, id, title, question):
        """
        Delete a mission from the memorization data.

        Parameters:
        - id (int): The ID of the memorization data.
        - title (str): The title of the memorization data.
        - question (str): The question to be deleted.

        Returns:
        - bool: True if the question is successfully deleted, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["memorization"]:
            for cont, item in enumerate(self.data["memorization"][id][title]["content"]):
                if item["question"] == question:
                    self.data["memorization"][id][title]["content"].pop(cont)
                    await self.save_data()
                    return True
            return False
        else:
            return False
    
    async def edit_misson(self, id, title, number, mode, answer, select_number=None):
        """
        Edit a mission in the memorization data.

        Args:
            id (str): The ID of the mission.
            title (str): The title of the mission.
            number (int): The number of the content to edit.
            mode (str): The mode of the content to edit.
            answer (str): The new answer for the content.
            select_number (int, optional): The number of the select option to edit (only applicable if mode is "select"). Defaults to None.

        Returns:
            bool: True if the mission was successfully edited, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["memorization"]:
            if title in self.data["memorization"][id]:
                edit_before = self.data["memorization"][id][title]["content"][number]
                if edit_before["mode"] == 0:
                    edit_before[mode] = answer
                elif edit_before["mode"] == 1:
                    if mode == "select":
                        edit_before["select"][select_number] = answer
                    else:
                        edit_before[mode] = answer
                self.data["memorization"][id][title]["content"][number] = edit_before
                await self.save_data()
                return True
            else:
                return False
        else:
            return False

    async def get_mission(self, id, title):
        """
        Get the content of a mission based on its ID and title.

        Parameters:
        - id (int): The ID of the mission.
        - title (str): The title of the mission.

        Returns:
        - content (list): The content of the mission if it exists, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["memorization"]:
            if title in self.data["memorization"][id]:
                return self.data["memorization"][id][title]["content"]
            else:
                return False
        else:
            return False
        

    async def get_mission_title(self, id):
        """
        Get the mission titles for a given ID.

        Args:
            id (str): The ID of the mission.

        Returns:
            list or bool: A list of mission titles if the ID exists in the data, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["memorization"]:
            return list(self.data["memorization"][id].keys())
        else:
            return False

    async def check_answer(self,id,title,question,answer):
        """
        Check the answer to a mission.

        Args:
            id (str): The ID of the mission.
            title (str): The title of the mission.
            question (str): The question of the mission.
            answer (str): The answer to the mission.

        Returns:
            bool: True if the answer is correct, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["memorization"]:
            if title in self.data["memorization"][id]:
                for item in self.data["memorization"][id][title]["content"]:
                    if item["question"] == question:
                        if item["answer"] == answer:
                            return True
                        else:
                            return False
                return False
            else:
                return False
        else:
            return False

    """
    user_status System ↓
    """

    async def add_user_status(self, id, title):
        """
        Add a user status to the user status data.

        Args:
            id (str): The ID of the user.
            title (str): The title of the mission.

        Returns:
            bool: True if the user status is added successfully, False otherwise.
        """
        self.data = await self.load_data()
        if not id in self.data["user_status"]:
            if not id in self.data["user_status"]:
                self.data["user_status"][id] = {title: {"userid": {"count": 0, "score": 0}}}
            return True
        else:
            return False
        
    async def edit_user_status(self, id, title, count, score):
        """
        Edit a user status in the user status data.

        Args:
            id (str): The ID of the user.
            title (str): The title of the mission.
            count (int): The count of the user status.
            score (int): The score of the user status.
        
        Returns:
            bool: True if the user status was successfully edited, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["user_status"]:
            if title in self.data["user_status"][id]:
                edit_before = self.data["user_status"][id][title]["userid"]
                edit_before["count"] += count
                edit_before["score"] += score
                self.data["user_status"][id][title]["userid"] = edit_before
                await self.save_data()
                return True
            else:
                return False
        else:
            return False
        
    async def get_user_status(self, id, title):
        """
        Get the user status of a user based on its ID and title.

        Args:
            id (str): The ID of the user.
            title (str): The title of the mission.

        Returns:
            dict: The user status of the user if it exists, False otherwise.
        """
        self.data = await self.load_data()
        if id in self.data["user_status"]:
            if title in self.data["user_status"][id]:
                return self.data["user_status"][id][title]["userid"]
            else:
                return False
        else:
            return False
