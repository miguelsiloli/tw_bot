import world 
from village_api import Vill
import datetime

class building:

    vill = Vill()
    world = world.world("pt62")

    def __init__(self, village_id: str, building: str):
        self.building = building
        self.village_id = village_id

    def _cost(self, flat: int, factor: float, level: int) -> int:
        return round(flat * factor ** (level-1))

    def _pop_cost(self, flat: int, factor: float, level: int) -> int:
        return(round(flat * factor ** (level-1)) - round(flat * factor ** (level-2)))

    @property
    def level(self) -> int:
        info = int(building.vill.village_info(self.village_id)["buildings"][self.building])
        return(info)

    @property
    def is_max_level(self) -> bool:

        if self.level == building.world.building(self.building)["max_level"]:
            return(True)
        else:
            return(False)

    @property
    def next_level_cost(self) -> dict:

        # add main building time reduction

        """
        returns -> {'wood': 2542, 'stone': 2569, 'iron': 1144, 'time': '6675'}
        """

        cost = {}
        if self.is_max_level:
            action_log("Building {self.building} is already at max level")    
            return({"wood": None, "stone": None, "iron": None, "time": None, "pop": None})

        next_level = int(self.level) + 1
        cost = {"wood": self._cost(int(building.world.building(self.building)["wood"]), float(building.world.building(self.building)["wood_factor"]), next_level),
                "stone": self._cost(int(building.world.building(self.building)["stone"]), float(building.world.building(self.building)["stone_factor"]), next_level),
                "iron": self._cost(int(building.world.building(self.building)["iron"]), float(building.world.building(self.building)["iron_factor"]), next_level),
                "time": self._cost(int(building.world.building(self.building)["build_time"]), float(building.world.building(self.building)["build_time_factor"]), next_level),
                "pop": self._pop_cost(int(building.world.building(self.building)["pop"]), float(building.world.building(self.building)["pop_factor"]), next_level )}

        return(cost)