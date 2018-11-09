from world import world
import sqlite3
import time

class Database:

    def __init__(self):
        self.connection = sqlite3.connect("pt62.db")
        self.cursor = self.connection.cursor()

class Player(Database):

    player_data = world("pt62").get_player()

    def __init__(self):
        super(Player, self).__init__()
    
    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Player (player_id INT, name TEXT, ally_id INT, num_vill INT, points INT, rank INT, datetime TEXT)")
        for key, item in Player.player_data.items():

            format = f"{item['player_id']}, '{item['name']}', {item['ally_id']}, {item['num_vill']}, {item['points']}, {item['rank']}, '{item['datetime']}'"

            self.cursor.execute(f"INSERT INTO Player VALUES({format})")

        self.connection.commit()
        self.cursor.close()

class Ally(Database):

    ally_data = world("pt62").get_ally()

    def __init__(self):
        super(Ally, self).__init__()

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Ally (ally_id INT, name TEXT, tag TEXT, members INT, points INT, total_points INT, rank INT, datetime TEXT)")
        for key, item in Ally.ally_data.items():

            try:
            
                format = f"{item['ally_id']}, '{item['name']}', '{item['tag']}', {item['members']}, {item['points']}, {item['total_points']}, {item['rank']}, '{item['datetime']}'"
                print(format)
                self.cursor.execute(f"INSERT INTO Ally VALUES({format})")

            except sqlite3.OperationalError:
                pass

        self.connection.commit()
        self.cursor.close()

class Village(Database):

    village_data = world("pt62").get_village()

    def __init__(self):
        super(Village, self).__init__()

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Village (village_id INT, name TEXT, x INT, y INT, continent INT, player_id INT, points INT, datetime TEXT)")
        for key, item in Village.village_data.items():

            try:
            
                format = f"{item['village_id']}, '{item['name']}', {item['x']}, {item['y']}, {item['continent']}, {item['player_id']}, {item['points']}, '{item['datetime']}'"
                print(format)
                self.cursor.execute(f"INSERT INTO Village VALUES({format})")

            except sqlite3.OperationalError:
                pass

        self.connection.commit()
        self.cursor.close()

class ODD(Database):

    odd_data = world("pt62").get_odd()

    def __init__(self):
        super(ODD, self).__init__()

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS ODD (player_id INT, points INT, rank INT, datetime TEXT)")
        for key, item in ODD.odd_data.items():

            try:
            
                format = f"{item['player_id']}, {item['points']}, {item['rank']}, '{item['datetime']}'"
                print(format)
                self.cursor.execute(f"INSERT INTO ODD VALUES({format})")

            except sqlite3.OperationalError:
                pass

        self.connection.commit()
        self.cursor.close()

class ODA(Database):

    oda_data = world("pt62").get_oda()

    def __init__(self):
        super(ODA, self).__init__()

    def update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS ODA (player_id INT, points INT, rank INT, datetime TEXT)")
        for key, item in ODA.oda_data.items():

            try:
            
                format = f"{item['player_id']}, {item['points']}, {item['rank']}, '{item['datetime']}'"
                print(format)
                self.cursor.execute(f"INSERT INTO ODA VALUES({format})")

            except sqlite3.OperationalError:
                pass

        self.connection.commit()
        self.cursor.close()

if __name__ == "__main__":
    while True:
        Player().update()
        Ally().update()
        Village().update()
        ODD().update()
        ODA().update()
        time.sleep(3600)
