rom tw_api_v2 import tw_api
from tw_log import action_log

# rework this class by scraping https://help.tribalwars.net/wiki

class building:

    _building_list = ["main", "farm", "storage", "place", "barracks", "smith", "wood", "stone",
                     "iron", "market", "stable", "wall", "garage", "hide", "snob", "statue"]

    _base_cost = {"main": {"wood": 90, "stone": 80, "iron": 70},
                     "barracks": {"wood": 200, "stone": 170, "iron": 90},
                     "stable": {"wood": 270, "stone": 240, "iron": 328},
                     "farm": {"wood": 45, "stone": 40, "iron": 30},
                     "storage": {"wood": 60, "stone": 50, "iron": 40},
                     "market": {"wood": 100, "stone": 80, "iron": 100},
                     "smith": {"wood": 220, "stone": 180, "iron": 240},
                     "wood": {"wood": 50, "stone": 60, "iron": 40},
                     "stone": {"wood": 65, "stone": 50, "iron": 40},
                     "iron": {"wood": 75, "stone": 65, "iron": 70}, 
                     "market": {"wood": 90, "stone": 80, "iron": 70},
                     "wall": {"wood": 50, "stone": 100, "iron": 20},
                     "garage": {"wood": 300, "stone": 240, "iron": 260},
                     "snob": {"wood": 90, "stone": 80, "iron": 70}}

    _base_points = {
        'main': 10,
        'barracks': 16,
        'stable': 24,
        'garage': 24,
        'church': 10,
        'church_f': 10,
        'snob': 512,
        'watchtower': 42,
        'smith': 19,
        'place': 0,
        'statue': 24,
        'market': 10,
        'wood': 6,
        'stone': 6,
        'iron': 6,
        'farm': 5,
        'storage': 6,
        'hide': 5,
        'wall': 8,
    }

    _max_level = {
        'main': 30,
        'barracks': 25,
        'stable': 20,
        'garage': 15,
        'church': 3,
        'church_f': 1,
        'snob': 1,
        'watchtower': 15,
        'smith': 20,
        'place': 1,
        'statue': 1,
        'market': 25,
        'wood': 30,
        'stone': 30,
        'iron': 30,
        'farm': 30,
        'storage': 30,
        'hide': 10,
        'wall': 20,
    }

    _cost_factor = {
        'main': 1.27,
        'barracks': 1.27,
        'stable': 1.27,
        'garage': 1.27,
        'church': 1.26,
        'church_f': 1,
        'snob': 1,
        'watchtower': 1.16,
        'smith': 1.27,
        'place': 1,
        'statue': 1,
        'market': 1.27,
        'wood': 1.27,
        'stone': 1.27,
        'iron': 1.27,
        'farm': 1.3,
        'storage': 1.27,
        'hide': 1.3,
        'wall': 1.27,
    }

    def __init__(self, building, village_id):

        # validate building
        self.building = building
        self.tw_api = tw_api 
        self.village_id = village_id
 
    def _cost(self, flat: int, factor: float, level: int) -> int:
        return round(flat * factor ** (level-1))

    @property
    def level(self) -> int:
        info = self.tw_api.village_info(village_id = self.village_id)["buildings"][self.building]
        return(info)

    @property
    def is_max_level(self) -> bool:
        if self.level == building._max_level.get(self.building):
            return(True)
        else:
            return(False)

    @property
    def next_level_cost(self) -> dict:

        cost = {}
        if self.is_max_level:
            action_log("Building {self.building} is already at max level")            

        next_level = int(self.level) +1
        cost = {"wood": self._cost(building._base_cost[self.building]["wood"], building._cost_factor[self.building], next_level),
                "stone": self._cost(building._base_cost[self.building]["stone"], building._cost_factor[self.building], next_level),
                "iron": self._cost(building._base_cost[self.building]["iron"], building._cost_factor[self.building], next_level)} 

        return(cost)
