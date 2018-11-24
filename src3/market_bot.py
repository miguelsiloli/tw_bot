from village_endpoint import Village_Endpoint
import sqlite3
import time

class Database:

    def __init__(self):
        self.connection = sqlite3.connect("market.db")
        self.cursor = self.connection.cursor()

class Trading_Bot(Database):
    
    _instance = Village_Endpoint().premium_stock("4284")
    _csrf_token = Village_Endpoint().csrf_token
    _gameword = Village_Endpoint().gameworld

    @property
    def ratios(self):
        ratios = {}
        res = ["wood", "stone", "iron"]
        for _res in res:
            rate = float(Trading_Bot._instance["response"]["rates"][_res])
            ratios.update({_res: 1/rate})

        return(ratios)

    @property
    def quantity_ratio(self):
        ratios = {}
        res = ["wood", "stone", "iron"]
        for _res in res:
            cap = float(Trading_Bot._instance["response"]["capacity"][_res])
            stock = float(Trading_Bot._instance["response"]["stock"][_res])
            ratios.update({_res: cap/stock})
        return(ratios)

    def sql_update(self):
        self.connection.execute("CREATE TABLE IF NOT EXISTS Market (time INT, ratio_wood REAL, ratio_stone REAL, ratio_iron REAL, cap_ration_wood REAL, cap_ration_stone REAL, cap_ration_iron REAL)")
        format = f"{time.time()}, {self.ratios['wood']}, {self.ratios['stone']}, {self.ratios['iron']}, {self.quantity_ratio['wood']}, {self.quantity_ratio['stone']}, {self.quantity_ratio['iron']}"
        self.cursor.execute(f"INSERT INTO Market VALUES({format})")
        self.connection.commit()
        self.cursor.close()



if __name__ == "__main__":
    while True:
        try:
            Trading_Bot().sql_update()
            time.sleep(5)
        except KeyboardInterrupt:
            break