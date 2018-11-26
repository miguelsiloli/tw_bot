# std lib dependancies
import time

# file dependencies
from session import Session
from api_exceptions import SessionException
from bs4 import BeautifulSoup

class Actions_Endpoint:

    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    _instance = Session("username", "password", "ptxx")

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

    def send_units(self, village_id: str, target_village: dict, units: dict, attack: bool = True ) -> None:
        
        """ target_village = {x: 123, y:123} 
            units -> {"spear": "", "sword": "", "axe": "", "archer": "", "spy": "", "light": "",
                        "marcher": "", "heavy", "ram": "", "catapult": "", "knight": "", "snob": ""} 
            attack = False -> support """

        if attack == True:
            endpoint_0 = "attack=1"
            endpoint_1 = "attack=true"
        else:
            endpoint_0 = "support=l"
            endpoint_1 = "support=true"

        x = target_village.get("x")
        y = target_village.get("y")

        def coord_format(target_village:dict):

            """ format coordinates -> 123|123 """

            return (f"{x}|{y}")
        
        def parser(url: str):

            """ find and urlencode ch token """

            soup = BeautifulSoup(url, 'html.parser')
            ch = list(soup.find_all("input"))[1]["value"]
            ch = ch.split(":")
            ch = ch[0] + "%3A" + ch[1]
            return(ch)

        target = coord_format(target_village)
        

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajax=confirm&h={self.csrf_token}&client_time={self.time}"
        body = f"0c365b7c2c49afe4e16108=4f6e51c90c365b&template_id=&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&x={target_village.get('x')}&y={target_village.get('y')}&input=&{endpoint_0}"

        with self.session as ses:

            # send attack
            res = ses.post(base_url, data = body, allow_redirects=True)
            response = res.json()["response"]["dialog"]

            # parse ch token from the attack request response
            ch_token = parser(response)
            
            # confirm attack
            base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajaxaction=popup_command&h={self.csrf_token}&client_time={self.time}"
            body = f"{endpoint_1}&ch={ch_token}&x={x}&y={y}&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&building=main"

            res = ses.post(base_url, data = body, allow_redirects=True)
            if res.status_code == 200:
                print(f"Attack order sent successful! from: {village_id} to: {target} units: {units}")

    def sell_resources(self, village_id: str, quantity: str, threshold: int, resource: str):

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&ajaxaction=exchange_begin&h={self.csrf_token}&client_time={self.time}"

        body = f"sell_{resource}={quantity}"

        with self.session as ses:

            res = ses.post(base_url, data = body, allow_redirects=True)
            response = res.json()["response"][0]
            rate_hash = response["rate_hash"]
            amount = abs(response["amount"])
            if response["amount"]/response["cost"] <= threshold:

                base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&ajaxaction=exchange_confirm&h={self.csrf_token}&client_time={self.time}"

                body = f"rate_{resource}={rate_hash}&sell_stone={amount}&mb=1"

                res = ses.post(base_url, data = body, allow_redirects=True) 

            else:
                pass

    def cancel_command(self, village_id: str, attack_id: str):

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajaxaction=cancel&h={self.csrf_token}&client_time={self.time}"

        body = f"id={attack_id}&village={village_id}"

        with self.session as ses:

            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(res.text) # okay

time.sleep(13000)
Actions_Endpoint()
units = {"spear": "0", "sword": "0", "axe": "2100", "archer": "0", "spy": "0", "light": "750", "marcher": "0", "heavy": "0", "ram": "100", "catapult": "0", "knight":"1","snob":"0"}
target = {"x": 407, "y":467}
time.sleep(12200)
Actions_Endpoint().send_units("4284", target, units)
#Actions_Endpoint().sell_resources("4284", "100", 1, "wood")
#print(Actions_Endpoint().cancel_command("4284"))
