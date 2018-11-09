import requests
import xmltodict
from urllib.parse import unquote
from datetime import datetime


class world:

    """
    {   
        # properties

        "worldspeed": returns int world speed,

        # getters

        "building": returns building stats,
        "unit": returns unit data,
        "get_village": returns data about all villages in the world,
        "get_player": returns data on all players alive in the world,
        "get_ally": returns data on all the tribes,
        "get_odd": returns data of defensive pontuation of all players alive,
        "get_oda": returns data of offensive pontuation of all players alive
    }
    """

    _world = "tribalwars.com.pt"

    def __init__(self, gameworld: str):
        self.building_config = f"https://{gameworld}.{world._world}/interface.php?func=get_building_info"
        self.gameworld_config = f"https://{gameworld}.{world._world}/interface.php?func=get_config"
        self.unit_config = f"https://{gameworld}.{world._world}/interface.php?func=get_unit_info"
        self.player_data = f"https://{gameworld}.{world._world}/map/player.txt"
        self.ally_data = f"https://{gameworld}.{world._world}/map/ally.txt"
        self.kill_def = f"https://{gameworld}.{world._world}/map/kill_def.txt"
        self.kill_att = f"https://{gameworld}.{world._world}/map/kill_att.txt"
        self.village_data = f"https://{gameworld}.{world._world}/map/village.txt"

    @property
    def worldspeed(self) -> int:      
        gameworld_config = xmltodict.parse(requests.get(self.gameworld_config).text)
        return({"speed": gameworld_config["config"]["speed"]})

    def building(self, building: str) -> dict:

        """
        OrderedDict([('max_level', '20'), ('min_level', '0'), ('wood', '270'), ('stone', '240'), ('iron', '260'), ('pop', '8'), 
                     ('wood_factor', '1.26'), ('stone_factor', '1.28'), ('iron_factor', '1.26'), ('pop_factor', '1.17'), 
                     ('build_time', '6000'), ('build_time_factor', '1.2')])
        """
        _building_list = ["main", "farm", "storage", "place", "barracks", "church", "smith", "wood", "iron", "stone", "market", "garage", "hide", "snob", "statue", "watchtower"]
        building_config = xmltodict.parse(requests.get(self.building_config).text)
        return(building_config["config"][building])

    def unit(self, unit: str) -> dict:

        """
        OrderedDict([('build_time', '1020'), ('pop', '1'), ('speed', '18.000000000504'), ('attack', '10'), ('defense', '15'), 
                     ('defense_cavalry', '45'), ('defense_archer', '20'), ('carry', '25')])
        """

        unit_config = xmltodict.parse(requests.get(self.unit_config).text)
        return(unit_config["config"][unit])

    def get_village(self):

        """
        '47199': {
          'village_id': '47199',
          'name': 'Aldeia de rpcg980',
          'x': '469',
          'y': '696',
          'continent': '64',
          'player_id': '265454'
          'points': '26'
        }
        """

        def parser(data:str):
            info = {}
            for row in data.splitlines():
                _info = row.split(",")
                info.update({_info[0]: 
                                {"village_id": _info[0],
                                "name": _info[1],
                                "x": _info[2],
                                "y": _info[3],
                                "continent": _info[3][:1]+_info[2][:1],
                                "player_id": _info[4],
                                "points": _info[5],
                                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))}})
            return(info)

        data = unquote(requests.get(self.village_data).text).replace("+", " ")
        return parser(data)

    def get_player(self):

        """
          '455936': {
            'player_id': '455936',
            'name': 'marco faria',
            'ally_id': '2736',
            'num_vill': '2',
            'points': '908',
            'rank': '1659'
          },
        """

        def parser(data:str):
            info = {}
            for row in data.splitlines():
                _info = row.split(",")
                info.update({_info[0]: 
                                {"player_id": _info[0],
                                "name": _info[1],
                                "ally_id": _info[2],
                                "num_vill": _info[3],
                                "points": _info[4],
                                "rank": _info[5],
                                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))}})

            return(info)


        data = unquote(requests.get(self.player_data).text).replace("+", " ")
        return parser(data)

    def get_ally(self):

        """
          '4': {
            'ally_id': '4',
            'name': 'Vai Tudo Abaixo ...',
            'tag': 'VT@',
            'members': '40',
            'num_vill': '3360',
            'points': '29194494',
            'total_points': '29194494',
            'rank': '1'
          },
        """

        def parser(data:str):
            info = {}
            for row in data.splitlines():
                _info = row.split(",")
                info.update({_info[0]: 
                                {"ally_id": _info[0],
                                "name": _info[1],
                                "tag": _info[2],
                                "members": _info[3],
                                "num_vill": _info[4],
                                "points": _info[5],
                                "total_points": _info[6],
                                "rank": _info[7],
                                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))}})

            return(info)


        data = unquote(requests.get(self.ally_data).text).replace("+", " ")
        return parser(data)

    def get_odd(self):

        """
          '351544': {
            'rank': '1150',
            'player_id': '351544',
            'points': '53328'
          },
        """

        def parser(data:str):
            info = {}
            for row in data.splitlines():
                _info = row.split(",")
                info.update({_info[1]: 
                                {"rank": _info[0],
                                "player_id": _info[1],
                                "points": _info[2],
                                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))}})

            return(info)

        data = unquote(requests.get(self.kill_def).text).replace("+", " ")
        return parser(data)

    def get_oda(self):

        """
          '352972': {
            'rank': '1222',
            'player_id': '352972',
            'points': '6790'
          },
        """

        def parser(data:str):
            info = {}
            for row in data.splitlines():
                _info = row.split(",")
                info.update({_info[1]: 
                                {"rank": _info[0],
                                "player_id": _info[1],
                                "points": _info[2],
                                "datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))}})

            return(info)

        data = unquote(requests.get(self.kill_att).text).replace("+", " ")
        return parser(data)


