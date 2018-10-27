# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 14:13:36 2018

@author: Geral
"""

import time
import select
from client import client
from bs4 import BeautifulSoup


# maybe making functions return status_code to troubleshoot 
# if building order wasnt executed due to client-server fault 
# or for specific in game reasons

class tw_api():
    
    def __init__(self, username:str, password:str, gameworld: str):
        self.username = username
        self.password = password
        self.gameworld = gameworld
        self.session = client().session
        self.time = str(int(time.time()))
        self._csrf_token = None
        self._session_id = None
    
    @property
    def session_id(self):
        """ retrieves sid """
        try:
            if not self._session_id:
                village_id = self.session.cookies.get("global_village_id")
                url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"
                res = self.session.get(url)
                self._session_id = self.session.cookies.get_dict().get("sid")
                return(self._session_id)

        except:
            self.login() 
            self.session_id()

    def login(self):

        """         <login>       """

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Firefox/64.0"}

        self.session.headers = headers

        with self.session as ses:

            # get page cookies
            url = "https://www.tribalwars.com.pt"
            res = ses.get(url)
            
            # authentification
            authurl = "https://www.tribalwars.com.pt/page/auth"
            data = f"username={self.username}&password={self.password}&remember=1"
            res = self.session.post(authurl, data=data, allow_redirects=False)

            if res.json()["status"] == "success":

                # retrieve login token
                url_gameworld = f"https://www.tribalwars.com.pt/page/play/{self.gameworld}"
                res = self.session.get(url_gameworld, allow_redirects=False)
                url_token = res.json()["uri"] # returns redirect link
  
                # get global village cookie
                res = self.session.get(url_token)
                village_id = res.cookies.get_dict().get("global_village_id")
                session_id = self.session.cookies.get_dict().get("sid")
                print(self.session.cookies.get_dict())

                self.session.headers['TribalWars-Ajax'] = '1'

                # logged in
                url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"
                res = self.session.get(url)

                # get h token
                h = res.json()['game_data']['csrf']
                self._csrf_token = h

                if res.status_code == 200:
                    print("Login successful!")

            else:
                print("Wrong username & password combination")

    def train(self, village_id: str, view: str, unit:str, amount: str) -> None:
        
        """ units = [spear, sword, axe, archer -> barracks
                     spy, light, marcher, heavy -> stable
                     ram, catapult -> workshop
                     knight -> statue
                     snob -> snob
                     militia -> farm] """
    
        # accessing class property      
        csrf_token = self._csrf_token
        print(csrf_token)
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable&ajaxaction=train&mode=train&h={csrf_token}&&client_time={int(time.time())}"
        body = f"units%5B{unit}%5D={amount}"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Train order sent successful!")

    def build(self, village_id: str, building: str ) -> None:
        
        # accessing class property      
        csrf_token = self._csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main&ajaxaction=upgrade_building&type=main&h={csrf_token}&&client_time={int(time.time())}"
        body =   f"id={building}&force=1&destroy=0&source=5854"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Build order sent successful!")

    def get_data(self, village_id:str) -> dict:
        
        units = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview&ajax=widget&widget=units&client_time={self.time}"
        village = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview" 
        buildings = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main"
        stable = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable"
        barracks = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=barracks&spear=0&sword=0&axe=0&archer=0&_partial"
        
        with self.session as ses:
            village = ses.get(village).text
            units = ses.get(units).text
            buildings = ses.get(buildings).text
            stable = ses.get(stable).text
            barracks = ses.get(barracks).json()["content"]
            
        return ({"units": units, "buildings": buildings, 
               "stable": stable, "barracks": barracks, "village": village})

    def attack(self, village_id: str, target_village: dict, units: dict, attack: bool = True ) -> None:
        
        """ target_village = {x: 123, y:123} 
            units -> {"spear": "", "sword": "", "axe": "", "archer": "", "spy": "", "light": "",
                        "marcher": "", "heavy", "ram": "", "catapult": "", "knight": "", "snob": ""} 
            attack = False -> support """

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

        sid = self.session_id.strip("%")
        csrf_token = self._csrf_token  
        print(csrf_token)
        

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajax=confirm&h={csrf_token}&client_time={self.time}"
        body = f"0c365b7c2c49afe4e16108=4f6e51c90c365b&template_id=&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&x={target_village.get('x')}&y={target_village.get('y')}&input=&attack=l"

        with self.session as ses:

            # send attack
            res = ses.post(base_url, data = body, allow_redirects=True)
            response = res.json()["response"]["dialog"]

            # parse ch token from the attack request response
            ch_token = parser(response)
            
            # confirm attack
            base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajaxaction=popup_command&h={csrf_token}&client_time={self.time}"
            body = f"attack=true&ch={ch_token}&x={x}&y={y}&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&building=main"

            print(base_url, body)

            res = ses.post(base_url, data = body, allow_redirects=True)

            if res.status_code == 200:
                print("Attack order sent successful!")

    def create_market_offer(self, village_id:str, sell: str, res_sell: str, buy: str, res_buy: str, offers: str, max_time: str = "8"):

        """ village_id -> target village id
            sell -> quantity to sell per offer
            res_sell -> resource to sell: iron, stone, wood
            buy -> quantity to buy per offer
            res_buy -> resource to buy: iron, stone, wood
            offers -> number of offers,
            max_time -> maximum distance time  """

        csrf_token = self._csrf_token

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&mode=own_offer&action=new_offer&h={csrf_token}"
        body = f"sell={sell}&res_sell={res_sell}&buy={buy}&res_buy={res_buy}&multi={offers}&max_time={max_time}"

        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Market order sent successful!")


    def send_resources(self, village_id:str, target_village: dict, wood: str = 0, stone: str = 0, iron: str = 0):

        """ village_id -> from village id
            target_village ->  {"x": x, "y":y}
            wood -> wood quantity
            stone -> stone quantity
            iron -> iron quantity """

        x = target_village.get("x")
        y = target_village.get("y")
        csrf_token = self._csrf_token

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&mode=send&try=confirm_send"
        body = f"wood={wood}&stone={stone}&iron={iron}&x={x}&y={y}&target_type=coord&input="

        def parser(url: str):
            soup = BeautifulSoup(url, 'html.parser')
            target_id = list(soup.find_all("input"))[1]["value"]
            return(target_id)

        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            target_id = parser(res.text)

            base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&action=send&h={csrf_token}"
            body = f"target_id={target_id}&wood={wood}&stone={stone}&iron={iron}"

            res = ses.post(base_url, data=body, allow_redirects = False)

            if res.status_code == 200:
                print("Resources sent successful!")
                
