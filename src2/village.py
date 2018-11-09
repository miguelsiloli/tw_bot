from tw_api_v3 import tw_api
from building_v2 import building
from tw_log import action_log
from api_get import API_get
class village():

    def __init__(self, village_id:str):
        self.tw_api = API_get()
        self.village_id = village_id

    """ VILLAGE PROPERTIES """

    @property
    def resources(self) -> dict:

        """ returns existing materials in village
            {'wood': 46576, 'stone': 294454, 'iron': 258766} """

        return({"wood": round(tw_api.village_info(self.village_id)["wood"]),
               "stone": round(tw_api.village_info(self.village_id)["stone"]),
               "iron": round(tw_api.village_info(self.village_id)["iron"])})

    @property
    def coordinates(self) -> dict:

        """ returns dict -> {'x': 466, 'y': 685} """

        return({"x": tw_api.village_info(self.village_id)["x"],
                "y": tw_api.village_info(self.village_id)["y"]})

    @property
    def population(self) -> dict:
        pass

    @property
    def name(self) -> str:

        """ returns str -> 060 ~ SkyZarD """

        return(tw_api.village_info(self.village_id)["name"])

    @property
    def merchants(self) -> dict:

        """ returns dict -> {'merchant_available': '3', 'merchant_total': '3'} """

        return(tw_api.merchant_status(self.village_id))

    @property
    def storage(self) -> str:

        """ returns str -> 3454 """

        return(tw_api.village_info(self.village_id)["storage_max"])

    @property
    def queues(self) -> str:

        return({"construction_queue": tw_api.construction_queue(self.village_id),
                "stable_queue": tw_api.stable_queue(self.village_id),
                "barracks_queue": tw_api.barracks_queue(self.village_id),
                "garage_queue": tw_api.garage_queue(self.village_id)})

    """ VILLAGE METHODS """

    def build(self, _building: str) -> None:

        """ building_list = [main, farm, storage, place, barracks, smith, wood, stone,
                             iron, market, stable, wall, garage, hide, snob, statue]

            returns none if the order is successful, 
            else returns missing resources
            {'wood': -392, 'stone': 459, 'iron': 277}
            # just show the missing resources
        """
        _cost = building(_building, self.village_id).next_level_cost

        if _cost["wood"] < self.resources["wood"] and _cost["stone"] < self.resources["stone"] and _cost["iron"] < self.resources["iron"]:
            pass            

        else:
            return({"wood": self.resources["wood"] - _cost["wood"],
                   "stone": self.resources["stone"] - _cost["stone"],
                   "iron": self.resources["iron"] - _cost["iron"]})

        has_premium = bool(tw_api.premium_features(self.village_id)["Premium"]["active"])

        if has_premium:
            c_queue = self.queues["construction_queue"]
            if len(c_queue[1]) == 4:
                action_log("Contruction queue full in village {self.name}")
                return({})
            else:
                return(self.tw_api.build(self.village_id, _building))

        else:
            c_queue = self.queues["construction_queue"]
            if len(c_queue[1]) == 1:
                action_log("Contruction queue full in village {self.name}")
                return({})
            else:
                return(self.tw_api.build(self.village_id, _building))


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


vil = village("40568")
vil.build("market")
#units = {"spear":"1", "sword": "1", "axe": "1", "archer": "1", "light": "1", "spy": "1", "marcher": "0", "heavy": "0", "ram": "1", "catapult": "0"}
#vil.train(units)
#vil.troops()

