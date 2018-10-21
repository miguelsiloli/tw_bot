# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 14:13:36 2018

@author: Geral
"""

import time
from client import client
from tw_api_exception import tw_api_exception

class tw_api():
    
    def __init__(self, username: str, password: str, gameworld: str):
        self.username = username
        self.password = password
        self.gameworld = gameworld
        self.session = client().session
        self._game_data = None
        
    
    @property
    def game_data(self):
        """ this property ensures the user is always logged in
            and updates self._game_data with game data """
        
        if isinstance(self._game_data, dict):
            pass
        
        else:
            self._game_data = self.login()
            
        return(self._game_data)
    
    @property
    def csrf_token(self):
        data = self.game_data  
        csrf_token = data['game_data']['csrf']   
        return(csrf_token)
        
    def login(self):
            
        self.session.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.session.headers["X-Requested-With"] = "XMLHttpRequest"
        
        # get page cookies
        url = "https://www.tribalwars.com.pt"
        res = self.session.get(url)
        
        # login to account
        authurl = "https://www.tribalwars.com.pt/page/auth"
        data = f"username={self.username}&password={self.password}&remember=1"
        res = self.session.post(authurl, data=data, allow_redirects=False)
        
        # login to gameworld
        url_gameworld = f"https://www.tribalwars.com.pt/page/play/{self.gameworld}"
        res = self.session.get(url_gameworld)
        
        # get the url encoded token
        url_token = res.json()["uri"]

        # res has all the information of the player including
        res = self.session.get(url_token)
        village_id = res.cookies.get_dict().get("global_village_id")
        self.session.headers['TribalWars-Ajax'] = '1'
        
        # logged into game
        # get gameworld data
        now = int(time.time())
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={now}"
        
        # has all the info but in json format
        res = self.session.get(url)
        game_data = res.json()
        
        return (game_data)
    

    def build(self, building: str, village_id: str) -> None:
        
        # accessing class property      
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main&ajaxaction=upgrade_building&type=main&h={csrf_token}&&client_time={int(time.time())}"
        body =   f"id={building}&force=1&destroy=0&source=5854"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)
            self.handle_response(res, content = True)

    
    def train(self, village_id: str, view: str, unit:str, amount: str) -> None:
        """ units = [spear, sword, axe, archer -> barracks
                     spy, light, marcher, heavy -> stable
                     ram, catapult -> workshop
                     knight -> statue
                     snob -> snob
                     militia -> farm] """
    
        # accessing class property      
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable&ajaxaction=train&mode=train&h={csrf_token}&&client_time={int(time.time())}"
        body = f"units%5B{unit}%5D={amount}"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)
            self.handle_response(res, content = True)
    
    def farm(self, village_id:str) -> None:
        
        url = "https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=am_farm&ajax=page_entries&Farm_page=1&class=row_a&extended=1&client_time=1"     
        
        #send request
        with self.session as ses:
            res = ses.get(url)
            self.handle_response(res)
    
    def handle_response(self, response: str, content: bool = False) -> None:
        
        if not str(response.status_code).startswith("2"):
            raise tw_api_exception(response)
            
        if content == True:
            print(response.content)
        
        else:
            print({"status":"success"})
