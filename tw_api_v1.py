import time
from client import client

class tw_api():
    
    def __init__(self, username:str, password:str, gameworld: str):
        self.username = username
        self.password = password
        self.gameworld = gameworld
        self.session = client().session
        self.time = time.time()
        self._csrf_token = None

    @property
    def csrf_token(self):

        if not self._csrf_token:
            village_id = self.session.cookies.get("global_village_id")
            url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"
            res = self.session.get(url)
            csrf_token = res.json()['game_data']['csrf'] 
            return(csrf_token)

        else:
            self.login()

    def login(self):

        """         <login>       """

        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "X-Requested-With": "XMLHttpRequest",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0"}

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

                self.session.headers['TribalWars-Ajax'] = '1'

                # logged in
                url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"
                res = self.session.get(url)

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
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable&ajaxaction=train&mode=train&h={csrf_token}&&client_time={int(time.time())}"
        body = f"units%5B{unit}%5D={amount}"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Train order sent successful!")
