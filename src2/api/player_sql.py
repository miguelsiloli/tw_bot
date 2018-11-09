# std lib
import sqlite3
import time
from datetime import datetime

# file imports
from api_get import User_Endpoint
from village_api import Vill
from building import building

class Database:

    def __init__(self):
        self.connection = sqlite3.connect("player_pt62.db")
        self.cursor = self.connection.cursor()

class Village(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Village, self).__init__()

    def _prep_dict(self, village_id: str):
        data = {}
        data["village_id"] = Village.vill.village_info(village_id)["id"]
        data["name"] = Village.vill.village_info(village_id)["name"]
        data["x"] = Village.vill.village_info(village_id)["x"]
        data["y"] = Village.vill.village_info(village_id)["y"]
        data["points"] = Village.vill.village_info(village_id)["points"]
        data["pop"] = Village.vill.population(village_id)["pop"]
        data["max_pop"] = Village.vill.population(village_id)["max_pop"]
        data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return data

    
    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Village (player_id INT, name TEXT, x INT, y INT, points INT, pop INT, max_pop INT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            data = self._prep_dict(_key)

            format = f"{data['village_id']}, '{data['name']}', {data['x']}, {data['y']}, {data['points']}, {data['pop']}, {data['max_pop']}, '{data['datetime']}'"

            self.cursor.execute(f"INSERT INTO Village VALUES({format})")

        self.connection.commit()
        self.cursor.close()

class Resources(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Resources, self).__init__()

    def _prep_dict(self, village_id: str):
        data = {}
        data["village_id"] = Village.vill.village_info(village_id)["id"]
        data["wood"] = int(Village.vill.village_info(village_id)["wood_float"])
        data["stone"] = int(Village.vill.village_info(village_id)["stone_float"])
        data["iron"] = int(Village.vill.village_info(village_id)["iron_float"])
        try:
            data["wood_per_hour"] = int(Village.vill.village_info(village_id)["wood_prod"]*Village.vill.village_info(village_id)["bonus"]["wood"]*3600)
        except:
            data["wood_per_hour"] = int(Village.vill.village_info(village_id)["wood_prod"]*3600)
        try:
            data["stone_per_hour"] = int(Village.vill.village_info(village_id)["stone_prod"]*Village.vill.village_info(village_id)["bonus"]["stone"]*3600)
        except:
            data["stone_per_hour"] = int(Village.vill.village_info(village_id)["stone_prod"]*3600)
        try:
            data["iron_per_hour"] = int(Village.vill.village_info(village_id)["iron_prod"]*Village.vill.village_info(village_id)["bonus"]["iron"]*3600)
        except:      
            data["iron_per_hour"] = int(Village.vill.village_info(village_id)["iron_prod"]*3600)
        data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return data

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Resources (village_id INT, wood INT, stone INT, iron INT, wood_per_hour INT, stone_per_hour INT, iron_per_hour INT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            data = self._prep_dict(_key)

            format = f"{data['village_id']}, {data['wood']}, '{data['stone']}', {data['iron']}, {data['wood_per_hour']}, {data['stone_per_hour']}, {data['iron_per_hour']}, '{data['datetime']}'"

            self.cursor.execute(f"INSERT INTO Resources VALUES({format})")

        self.connection.commit()
        self.cursor.close()

class Stable(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Stable, self).__init__()

    def _prep_dict(self, _data: dict):
        data = {}
        for _key, _item in _data.items():
            data["unit"] = _key
            data["quantity"] = _item["quantity"]
            data["duration"] = _item["duration"]
            data["date_completion"] = _item["date_completion"]
            data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return data



    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Stable (village_id INT, unit TEXT, quantity INT, duration TEXT, date_completion TEXT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            queue = Village.vill.stable_queue(_key)
            for element in queue:
                data = self._prep_dict(element)

                format = f"{_key}, '{data['unit']}', {data['quantity']}, '{data['duration']}', '{data['date_completion']}', '{data['datetime']}'"

                self.cursor.execute(f"INSERT INTO Stable VALUES({format})")

        self.connection.commit()
        self.cursor.close() 

class Barracks(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Barracks, self).__init__()

    def _prep_dict(self, _data: dict):
        data = {}
        data["village_id"] = Village.vill.village_info(village_id)["id"]
        data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return data



    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Barracks (village_id INT, unit TEXT, quantity INT, duration TEXT, date_completion TEXT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            queue = Village.vill.barracks_queue(_key)
            for element in queue:
                data = self._prep_dict(element)

                format = f"{_key}, '{data['unit']}', {data['quantity']}, '{data['duration']}', '{data['date_completion']}', '{data['datetime']}'"

                self.cursor.execute(f"INSERT INTO Barracks VALUES({format})")

        self.connection.commit()
        self.cursor.close() 

class Garage(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Garage, self).__init__()

    def _prep_dict(self, _data: dict):
        data = {}
        for _key, _item in _data.items():
            data["unit"] = _key
            data["quantity"] = _item["quantity"]
            data["duration"] = _item["duration"]
            data["date_completion"] = _item["date_completion"]
            data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return data



    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Garage (village_id INT, unit TEXT, quantity INT, duration TEXT, date_completion TEXT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            queue = Village.vill.garage_queue(_key)
            for element in queue:
                data = self._prep_dict(element)

                format = f"{_key}, '{data['unit']}', {data['quantity']}, '{data['duration']}', '{data['date_completion']}', '{data['datetime']}'"

                self.cursor.execute(f"INSERT INTO Garage VALUES({format})")

        self.connection.commit()
        self.cursor.close() 

class Building(Database):

    vill = Vill()
    vill_list = User_Endpoint().number_of_villages()

    def __init__(self):
        super(Building, self).__init__()

    def _building(self, village_id: str):
        _building_list = ["main", "farm", "storage", "place", "barracks", "church", "smith", "wood", "iron", "stone", "market", "garage", "hide", "snob", "statue", "watchtower"]
        _data = Building.vill.village_info(village_id)["buildings"]
        data = {}

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Building (village_id INT, building TEXT, level INT, next_level TEXT, next_wood TEXT, next_stone INT, next_iron INT, next_time TEXT, next_pop INT, datetime TEXT)")

        for _key, _item in Village.vill_list.items():
            print(_key)
            _data1 = Building.vill.village_info(_key)
            _data = _data1["buildings"]        
            for _key, _item in _data.items():
                if _key != "village":
                    try:
                        data = {}
                        data["village_id"] = _data1["id"]
                        data["building"] = _key
                        data["level"] = _item
                        if building(_data1["id"], _key).is_max_level:
                            print(building(_data1["id"], _key).is_max_level)
                            data["next_level"] = _item
                        else:
                            data["next_level"] = int(_item) +1
                        _call = building(_data1["id"], _key).next_level_cost
                        data["next_wood"] = _call["wood"]
                        data["next_stone"] = _call["stone"]
                        data["next_iron"] = _call["iron"]
                        data["next_time"] = _call["time"]
                        data["next_pop"] = _call["pop"]
                        data["datetime"] =  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        
                        format = f"{data['village_id']}, '{data['building']}', {data['level']}, {data['next_level']}, {data['next_wood']}, '{data['next_stone']}', '{data['next_iron']}', '{data['next_time']}', {data['next_pop']}, '{data['datetime']}'"
                        print(format)
                        self.cursor.execute(f"INSERT INTO Building VALUES({format})")

                    except KeyError as e:
                        print(e)
                        pass


        self.connection.commit()
        self.cursor.close() 


if __name__ == "__main__":
    #Village().update()
    #Resources().update()
    #Stable().update()
    #Barracks().update()
    #Garage().update()
    Building().update()


