from tw_api_v2 import tw_api
from building import building

class village():

    def __init__(self, village_id:str):
        self.tw_api = tw_api
        self.village_id = village_id
        # name
        # coordinates
        # etc as properties

    @property
    def resources(self) -> dict:

        """ returns existing materials in village
            {'wood': 46576, 'stone': 294454, 'iron': 258766} """

        return({"wood": round(tw_api.village_info(self.village_id)["wood"]),
               "stone": round(tw_api.village_info(self.village_id)["stone"]),
               "iron": round(tw_api.village_info(self.village_id)["iron"])})

    @property
    def coordinates(self) -> dict:
        return({"x": tw_api.village_info()["x"],
                "y": tw_api.village_info()["y"]}

    def build(self, _building: str) -> None:

        """ building_list = [main, farm, storage, place, barracks, smith, wood, stone,
                             iron, market, stable, wall, garage, hide, snob, statue]

            returns none if the order is successful, 
            else returns missing resources
            {'wood': -392, 'stone': 459, 'iron': 277}
        """

        _cost = building(_building, self.village_id).next_level_cost

        if _cost["wood"] < self.resources["wood"] and _cost["stone"] < self.resources["stone"] and _cost["iron"] < self.resources["iron"]:
            print("Buildable")
            return(self.tw_api.build(self.village_id, _building))

        else:
            return({"wood": self.resources["wood"] - _cost["wood"],
                   "stone": self.resources["stone"] - _cost["stone"],
                   "iron": self.resources["iron"] - _cost["iron"]})

    def train(self, units: str) -> None:

        """ format: {"spear":"0", "sword": "0", "axe": "0", "archer": "0", "light": "1", "spy": "1", "marcher": "1", "heavy": "1", "ram": "1", "catapult": "0"} """ 
        
        for key, value in units.items():

            if key in ["spear", "sword", "axe", "archer"]:
                view = "barracks"
                
            elif key in ["spy", "light", "marcher", "heavy"]:
                view = "stable"

            elif key in ["ram", "catapult"]:
                view = "workshop"

            self.tw_api.train(self.village_id, view, key, value)
