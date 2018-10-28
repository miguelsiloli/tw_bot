import time
import datetime
from client import client
from bs4 import BeautifulSoup

# maybe making functions return status_code to troubleshoot 
# if building order wasnt executed due to client-server fault 
# or for specific in game reasons

# very basic api should include all features expect farm
# TODO: move parsing to a singleton
# improve parsers
# add logs
# add exception classes

class tw_api():
    
    def __init__(self, username:str, password:str, gameworld: str):
        self.username = username
        self.password = password
        self.gameworld = gameworld
        self.session = client().session
        self.time = time.time()
        self.csrf_token = None
        self.session_id = None
        self.datetime = datetime.datetime.now().strftime("%H:%M:%S")

    def login(self) -> None:

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


            try:

                res = self.session.post(authurl, data=data, allow_redirects=False)

                if res.json()["status"] == "success":

                    with self.session as ses:

                        # retrieve login token
                        url_gameworld = f"https://www.tribalwars.com.pt/page/play/{self.gameworld}"
                        res = ses.get(url_gameworld, allow_redirects=False)
                        url_token = res.json()["uri"] # returns redirect link
  
                        # get global village cookie
                        res = ses.get(url_token)
                        village_id = res.cookies.get_dict().get("global_village_id")
                        self.session_id = self.session.cookies.get_dict().get("sid").strip("%")

                        self.session.headers['TribalWars-Ajax'] = '1'

                        # logged in
                        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"
                        res = ses.get(url)

                    # get csrf_token token
                    self.csrf_token = res.json()['game_data']['csrf']

                    # check if login was successful
                    if res.status_code == 200 and self.csrf_token != None:
                        print(f"Login successful! -> {self.datetime}")

            except:
                print("Wrong username & password combination")

    def logout(self, village_id:str) -> None:

        """         <logout>       """
        
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=&action=logout&h={self.csrf_token}"

        with self.session as ses:

            res = ses.get(url)

        if res.status_code == 200:
            print(f"Logout successful! -> {self.datetime}")


    ##################          VILLAGE INFORMATION ENDPOINT        ##################        


    def troops(self, village_id:str) -> dict:

        """ returns a dictionary with the name and number of troops: 
            format : {"troops": quantity} """

        def parser(url:str) -> dict:

            """ format: units = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview&ajax=widget&widget=units&client_time={now}" 
                returns the number existing units in the village """

            units_list = ["spear", "sword", "axe", "archer",
                         "spy", "light", "marcher", "heavy",
                         "ram", "catapult",
                         "knight",
                         "snob",
                         "militia"]   

            soup = BeautifulSoup(url, 'html.parser')
            a = list(soup.find_all("strong")) 
            units = {}
            for element in a:
                element = element.find_parent("tr")
                count = 0
                for count in range(len(units_list)):
                    if units_list[count] in str(element.find(class_ = "unit_link")): 
                        units.update({units_list[count]: element.find("strong").text})

            return(units)

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview&ajax=widget&widget=units&client_time={self.time}"
        
        with self.session as ses:
            
            res = ses.get(url).json()["response"]
            return parser(res)

    def village(self, village_id: str) -> dict:

        """ returns village and buildings information """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url).json()["game_data"]
            return(res)

    def stable_queue(self, village_id:str) -> dict:

        """ returns the first training order """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable"

        def parser(url:str) -> dict:
            """ f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable" 
                returns the executing training queue but not other queued orders """
    
            units = ["Batedor", "Cavalaria leve", "Arqueiro a cavalo", "Cavalaria Pesada"]
    
            soup = BeautifulSoup(url, 'html.parser')

            try:

                queue = soup.find(id = "trainqueue_wrap_stable").find(class_ = "lit-item").text
                for unit in units:
                    if unit in queue:
                        quantity = [int(s) for s in queue.split() if s.isdigit()][0]
                        return({unit: quantity})  

            except AttributeError:

                return({}) # return empty dict if not training any unit

        with self.session as ses:

            res = ses.get(url)
            return parser(res.text)

    def barracks_queue(self, village_id: str) -> dict:

        """ returns the first training order """

        def parser(url:str) -> dict:
 
            """ f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=barracks&spear=0&sword=0&axe=0&archer=0&_partial"
                returns the executing training queue but not other queued orders """  
        
            units = ["Lanceiro", "Espadachim", "Viking", "Arqueiro"  ]
    
            soup = BeautifulSoup(url, 'html.parser')

            try:

                queue = soup.find(id = "trainqueue_wrap_barracks").find(class_ = "lit-item").text
                for unit in units:
                    if unit in queue:
                        quantity = [int(s) for s in queue.split() if s.isdigit()][0]
                        return({unit: quantity})

            except AttributeError:
                
                return({}) # return empty dict if not training any unit

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=barracks&spear=0&sword=0&axe=0&archer=0&_partial"   
            
        with self.session as ses:

                res = ses.get(url).json()["content"]
                return(parser(res))
    
    def construction_queue(self, village_id: str) -> dict:

        """ returns the first building queued order
            return the executing building order and time till completion """

        def parser(url:str) -> dict:

            """ format: buildings = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main" 
                returns the executing training queue and the name of the queued buildings """

            buildings_list = ["Mina de Ferro", "Edif�cio principal", "Quartel", "Est�bulo", "Oficina",
                              "Igreja", "Academia", "Ferreiro", "Pra�a de Reuni�es", 
                              "Est�tua", "Mercado", "Bosque", "Po�o de Argila", 
                              "Mina de Ferro", "Fazenda", "Armaz�m", "Muralha"]
    
            soup = BeautifulSoup(url, 'html.parser')

            try:
                buildqueue = soup.find_all(id = "buildqueue") # find building queue
                timer = soup.find("span", class_ = "timer")
                construction_queue = {}
                queue = []
                for element in list(buildqueue):
                    element = element.find_all(class_="lit-item")
                    for ele in element:
                        element = ele.text #ele.text) #building name #.find(class_="order-progress")
                        for count in range(len(buildings_list)):
                            if buildings_list[count] in element:  
                                queue.append(buildings_list[count])
                                if not construction_queue: # make sure you just get the first building                       
                                    construction_queue = {buildings_list[count+1]: timer.text}

                return(construction_queue, queue)

            except AttributeError:
                
                return ({}) # return empty dict if nothing is being built
        
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main"
            
        with self.session as ses:

                res = ses.get(url).text
                return(parser(res))

    def merchant_status(self, village_id:str) -> dict:

        """ returns the total number of merchants 
            returns the number of available merchants """

        def parser(url:str) -> dict:
            soup = BeautifulSoup(url, 'html.parser')
            merchant_available = soup.find(id = "market_merchant_available_count").text
            merchant_total = soup.find(id = "market_merchant_total_count").text
            return({"merchant_available": merchant_available, "merchant_total": merchant_total})

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&mode=traders"

        with self.session as ses:

                res = ses.get(url).text
                return(parser(res))


    ##################          VILLAGE ORDERS ENDPOINT        ################## 

    
    def build(self, village_id: str, building: str ) -> None:
        
        # accessing class property      
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main&ajaxaction=upgrade_building&type=main&h={csrf_token}&&client_time={int(time.time())}"
        body =   f"id={building}&force=1&destroy=0&source=5854"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Build order sent successful!")
                
    def train(self, village_id: str, view: str, unit:str, amount: str) -> None:
        
        """ units = [spear, sword, axe, archer -> barracks
                     spy, light, marcher, heavy -> stable
                     ram, catapult -> workshop
                     knight -> statue
                     snob -> snob
                     militia -> farm] """
       
        csrf_token = self._csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable&ajaxaction=train&mode=train&h={csrf_token}&&client_time={int(time.time())}"
        body = f"units%5B{unit}%5D={amount}"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                print("Train order sent successful!")                

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

        sid = self.session_id
        csrf_token = self.csrf_token  
        print(csrf_token)
        

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajax=confirm&h={csrf_token}&client_time={self.time}"
        body = f"0c365b7c2c49afe4e16108=4f6e51c90c365b&template_id=&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&x={target_village.get('x')}&y={target_village.get('y')}&input=&{endpoint_0}"

        with self.session as ses:

            # send attack
            res = ses.post(base_url, data = body, allow_redirects=True)
            response = res.json()["response"]["dialog"]

            # parse ch token from the attack request response
            ch_token = parser(response)
            
            # confirm attack
            base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&ajaxaction=popup_command&h={csrf_token}&client_time={self.time}"
            body = f"{endpoint_1}&ch={ch_token}&x={x}&y={y}&source_village={village_id}&spear={units.get('spear')}&sword={units.get('sword')}&axe={units.get('axe')}&archer={units.get('archer')}&spy={units.get('spy')}&light={units.get('light')}&marcher={units.get('marcher')}&heavy={units.get('heavy')}&ram={units.get('ram')}&catapult={units.get('catapult')}&knight={units.get('knight')}&snob={units.get('snob')}&building=main"

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
