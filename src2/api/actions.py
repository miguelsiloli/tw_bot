# std lib dependancies
import logging
import time

# file dependencies
from session import Session
from tw_log import action_log
from api_exceptions import SessionException

class Actions_Endpoint:

    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    _instance = Session("Seelfed", "azulcaneta7", "pt62")

    def __init__(self):

        if Actions_Endpoint._instance.verify_session():
            self.session = Actions_Endpoint._instance.get_session()
        else:
            self.session = Actions_Endpoint._instance.new_session()

        self.gameworld = Actions_Endpoint._instance.gameworld
        self.village_id = Actions_Endpoint._instance.village_id
        self.csrf_token = Actions_Endpoint._instance.csrf_token
        self.session_id = Actions_Endpoint._instance.session_id
        self.time = time.time()

    def build(self, village_id: str, building: str ) -> None:
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main&ajaxaction=upgrade_building&type=main&h={self.csrf_token}&&client_time={self.time}"
        body =   f"id={building}&force=1&destroy=0&source=5854"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException
            elif res.status_code == 200:
                action_log("Build order sent successful!") # done

#Actions_Endpoint().coin("25382", "1") #not working
#Actions_Endpoint().build("28077", "garage")
#units = {"spear": "0", "sword": "0", "axe": "0", "archer": "0", "spy": "25", "light": "0", "marcher": "0", "heavy": "0", "ram": "0", "catapult": "0", "knight":"0","snob":"0"}
