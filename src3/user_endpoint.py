# std lib dependancies
import logging
import time

# file dependencies
from session import Session
from tw_log import action_log

# module dependencies
from bs4 import BeautifulSoup


class User_Endpoint:
    """This class has methods with information that apply to the user.
        :method premium_features: returns information about which premium features are active and which are not
        :type: dict
        :method player_info: returns general information about the player
        :type: dict
        :method number_of_villages: returns all the village id's and names
        :type: dict
        :method incoming_attacks: returns data on incoming attacks
        :type: list of dict
        :method incoming_support: returns data on incoming support
        :type: list of dict
    """
    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    _instance = Session("username", "password", "ptxx")

    def __init__(self):

        if User_Endpoint._instance.verify_session():
            self.session = User_Endpoint._instance.get_session()
        else:
            self.session = User_Endpoint._instance.new_session()

        self.gameworld = User_Endpoint._instance.gameworld
        self.village_id = User_Endpoint._instance.village_id
        self.csrf_token = User_Endpoint._instance.csrf_token
        self.session_id = User_Endpoint._instance.session_id
        self.time = time.time()

    def premium_features(self) -> dict:
        """ :returns:
            {
              'Premium': {
                'possible': True,
                'active': True
              },
              'AccountManager': {
                'possible': True,
                'active': True
              },
              'FarmAssistent': {
                'possible': True,
                'active': True
              }
            } 
            :raises: SessionException
        """
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=api&ajax=resources_schedule&id={self.village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(res.json()["game_data"]['features']) # done

    def player_info(self) -> dict:
        """ :returns:
            {
              'id': '237776',
              'name': 'Seelfed',
              'ally': '1805',
              'ally_level': '10',
              'ally_member_count': '40',
              'sitter': '0',
              'sleep_start': '0',
              'sitter_type': 'normal',
              'sleep_end': '0',
              'sleep_last': '0',
              'email_valid': '1',
              'villages': '59',
              'incomings': '0',
              'supports': '0',
              'knight_location': '25248',
              'knight_unit': '610842885',
              'rank': 144,
              'points': '440086',
              'date_started': '1532186125',
              'is_guest': '0',
              'birthdate': '0000-00-00',
              'confirmation_skipping_hash': '',
              'quest_progress': '0',
              'points_formatted': '440<span class="grey">.</span>086',
              'rank_formatted': '144',
              'pp': '1377',
              'new_ally_application': '0',
              'new_ally_invite': '0',
              'new_buddy_request': '0',
              'new_daily_bonus': '0',
              'new_forum_post': '3',
              'new_igm': '0',
              'new_items': '2',
              'new_report': '0',
              'new_quest': '1'
            } 
            :raises: SessionException
        """
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=api&ajax=resources_schedule&id={self.village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(res.json()["game_data"]["player"]) # done

    def number_of_villages(self) -> dict:
        """ note::tested with premium
            :returns:
            {'25382': '001 ~ Oblivion', '25907': '002 ~ Lethal', '25599': '003 ~ Faith'}
            :raises: SessionException
        """

        if self.premium_features()["Premium"]["active"]:
            url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=overview_villages&mode=combined"
        else:
            url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=overview_villages"

        def parser(url:str):
            village_id = []
            village_name = []
            soup = BeautifulSoup(url, 'html.parser')
            now = list(soup.find_all(attrs={'class': 'quickedit-vn'}))
            for element in now:
                village_id.append(element["data-id"])
            then = list(soup.find_all(attrs={'class': 'quickedit-label'}))
            for element in then:
                village_name.append(element["data-text"])
 
            villages = dict(zip(village_id, village_name))
            return(villages)

        with self.session as ses:
            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

            return(parser(res.text)) # done

    def incoming_attacks(self) -> list:
        """ note::tested with premium
            :returns:
            [{'from': '004 ~ Hyper (481|655) K64', 'to': '028 ~ Tighten Up (484|664) K64', 'from_player': 'Seelfed', 'distance': '9.5', 'duration': '0:23:58'}, 
            {'from': '004 ~ Hyper (481|655) K64', 'to': '036 ~ chamk (482|666) K64', 'from_player': 'Seelfed', 'distance': '11.0', 'duration': '0:37:46'},  
            {'from': '004 ~ Hyper (481|655) K64', 'to': '036 ~ chamk (482|666) K64', 'from_player': 'Seelfed', 'distance': '11.0', 'duration': '0:37:54'}, 
            {'from': '004 ~ Hyper (481|655) K64', 'to': '040 ~ FIlIPE95 (473|675) K64', 'from_player': 'Seelfed', 'distance': '21.5', 'duration': '1:41:02'}, 
            :raises: SessionException
        """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=overview_villages&mode=incomings&subtype=attacks"

        def parser(url:str):

            lista = []
            soup = BeautifulSoup(url, 'html.parser')
            now = soup.find_all(attrs={'class': 'quickedit'})
            for element in now:
                element = element.find_parent("tr")
                ele = element.find_all("td")
                timer = element.find(attrs = {'class': 'timer'}).text
                element = list(element.find_all("a"))
                att = ({"from": element[3].text, "to": element[2].text, "from_player": element[4].text, "distance": ele[4].text.strip("\n").strip(" "), "duration": timer})
                lista.append(att)

            return(lista)

        with self.session as ses:
            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                 raise SessionException

        return(parser(res.text))

    def incoming_support(self) -> list:
        """ note::tested with premium
            :returns:
            [{'from': '064 ~ OldFox (471|658) K64', 'to': '025 ~ Bug (479|655) K64', 'from_player': 'Seelfed', 'distance': '8.5', 'duration': '1:12:31'}]
            :raises: SessionException
        """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={self.village_id}&screen=overview_villages&mode=incomings&subtype=supports"

        def parser(url:str):

            lista = []
            soup = BeautifulSoup(url, 'html.parser')
            now = soup.find_all(attrs={'class': 'quickedit'})
            for element in now:
                element = element.find_parent("tr")
                ele = element.find_all("td")
                timer = element.find(attrs = {'class': 'timer'}).text
                element = list(element.find_all("a"))
                att = ({"from": element[3].text, "to": element[2].text, "from_player": element[4].text, "distance": ele[4].text.strip("\n").strip(" "), "duration": timer})
                lista.append(att)

            return(lista)

        with self.session as ses:
            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                 raise SessionException

        return(parser(res.text))


