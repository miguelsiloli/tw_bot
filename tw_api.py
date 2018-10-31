import time
import datetime
from client import client
from bs4 import BeautifulSoup
from tw_log import action_log

# maybe making functions return status_code to troubleshoot 
# if building order wasnt executed due to client-server fault 
# or for specific in game reasons

class tw_api():
   
    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    def __init__(self, username:str, password:str, gameworld: str):
        self.username = username
        self.password = password
        self.gameworld = gameworld
        self.session = client().session
        self.time = time.time()
        self.csrf_token = None
        self.session_id = None
        self.datetime = datetime.datetime.now().strftime("%H:%M:%S")

    ##################                ACCOUNT MANAGEMENT            ################## 

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
                        action_log("Login successful!")

            except:
                action_log("Wrong username & password combination") # done

    def logout(self, village_id:str) -> None:

        """         <logout>       """
        
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=&action=logout&h={self.csrf_token}"

        with self.session as ses:

            res = ses.get(url)

        if res.status_code == 200:
            action_log(f"Logout successful!") # done

    def premium_features(self, village_id) -> dict:

        """ {
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
        """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url).json()["game_data"]['features']
            print(res)
            return(res) # done

    def player_info(self, village_id: str) -> dict:

        """ {
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
        """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url).json()["game_data"]["player"]
            print(res)
            return(res) # done

    def number_of_villages(self, village_id:str):

        """ tested with premium
            returns {village_id, village_name} """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview_villages"

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
            parser(res.text) # done

    ##################          VILLAGE INFORMATION ENDPOINT        ##################        

    # missing garage queue -> fixed
    # missing know which units where researched and which werent
    # snob queue and number of coined coins till next nobleman
    # defense power 
    # probably merge troops_in_village, troops_available; troops_out etc in one method            

    def troops_in_village(self, village_id:str) -> dict:

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

    def troops_available(self, village_id:str):

        """ troops in village and from village
            troops available for new orders """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&mode=units"
        unit_list = ["spear", "sword", "axe", "archer", "spy", "light", "marcher", "heavy", "ram", "catapult", "knight", "snob", "militia"]

        def parser(url:str):
            units = {}
            soup = BeautifulSoup(url, 'html.parser')
            village = soup.find(class_ = "unit-item-spear").find_parent("tr")
            village = list(village.find_all(class_ = "unit-item"))
            count = 0
            for element in village:
                units.update({unit_list[count]: element.text})
                count += 1
            return units 

        with self.session as ses:
            res = ses.get(url).text
            print(parser(res))
            return parser(res)

    def attack_power(self, village_id:str) -> dict:

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&mode=units&display=stats_att"
        stats = ["village", "general power", "cavalry power", "archer power"]

        def parser(url:str):
            attackpower = {}
            soup = BeautifulSoup(url, 'html.parser')
            village = soup.find_all(class_ = "hidden")[1]
            village = village.find_parent("tr")
            count = 0
            for td in village.select('td'):
                attackpower.update({stats[count]: td.text})
                count += 1
            attackpower.pop("village")
            return(attackpower)
 

        with self.session as ses:
            res = ses.get(url).text
            parser(res)

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview&ajax=widget&widget=units&client_time={self.time}"
        
        with self.session as ses:
            
            res = ses.get(url).json()["response"]
            return (parser(res))

    def village_info(self, village_id: str) -> dict:

        """ {
              'id': 27802,
              'name': '005 ~ Critical',
              'wood_prod': 1.53333335,
              'stone_prod': 1.53333335,
              'iron_prod': 1.53333335,
              'storage_max': 400000,
              'pop_max': 31363,
              'wood_float': 87056.80737,
              'stone_float': 104001.8074,
              'iron_float': 336208.8074,
              'wood': 87057,
              'stone': 104002,
              'iron': 336209,
              'pop': 31363,
              'x': 481,
              'y': 660,
              'trader_away': 0,
              'bonus_id': '4',
              'bonus': {
                'farm': 1.1,
                'wood': 1.15,
                'stone': 1.15,
                'iron': 1.15
              },
              'buildings': {
                'village': '27802',
                'main': '20',
                'farm': '30',
                'storage': '30',
                'place': '1',
                'barracks': '25',
                'church': '0',
                'church_f': '0',
                'smith': '20',
                'wood': '30',
                'stone': '30',
                'iron': '30',
                'market': '20',
                'stable': '20',
                'wall': '20',
                'garage': '5',
                'hide': '3',
                'snob': '1',
                'statue': '1',
                'watchtower': '0'
              },
              'player_id': '237776',
              'modifications': 1,
              'points': 9742,
              'last_res_tick': 1540988108000.0,
              'res': [
                87057,
                1.53333335,
                104002,
                1.53333335,
                336209,
                1.53333335,
                400000,
                31363,
                31363
              ],
              'coord': '481|660',
              'is_farm_upgradable': False
            } """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url).json()["game_data"]['village']
            print(res)
            return(res) # done

    def garage_queue(self, village_id:str) -> dict: # done

        """ returns a list of orders; each order is a dictionary
            [{'Catapulta': {'duration': '4:58:55', 'date_completion': 'amanhã às 03:01:27 horas', 'quantity': 10}}] 
        """
            
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=garage"

        def parser(url:str) -> dict:

            units = ["Ariete", "Catapulta"]

            soup = BeautifulSoup(url, 'html.parser')

            try:
                orders = []
                # find executing order
                timer = soup.find(id = "trainqueue_wrap_garage")
                timer = list(timer.find_all(attrs = {"class": "lit-item"}))

                queue = soup.find(id = "trainqueue_wrap_garage").find(class_ = "lit-item").text
                for unit in units:
                    if unit in queue:
                        quantity = [int(s) for s in queue.split() if s.isdigit()][0]
                        orders.append({unit:{"duration": timer[1].text, "date_completion": timer[2].text, "quantity": quantity}})

                # find other orders           
                queue = soup.find(id = "trainqueue_garage")

                queue = list(queue.find_all(attrs = {"class": "sortable_row"}))
                for element in queue:
                    lista = (list(element.find_all("td")))
                    for unit in units:
                        if unit in element.text:
                            quantity = [int(s) for s in element.text.split() if s.isdigit()][0]
                            orders.append({unit: {"duration": lista[1].text, "date_completion": lista[2].text, "quantity": quantity}})
                print(orders)
                return (orders)

            except AttributeError:
                
                return([]) # return empty list if not training any unit

        with self.session as ses:

            res = ses.get(url)
            return parser(res.text) # done

    def stable_queue(self, village_id:str) -> dict:

        """ returns the list of orders; each order is a dictionary
            [{'Cavalaria leve': {'duration': '0:16:08', 'date_completion': 'hoje às 20:30:11 horas', 'quantity': 6}}, 
             {'Cavalaria leve': {'duration': '1:02:22', 'date_completion': 'hoje às 21:32:33 horas', 'quantity': 20}}]"""
            
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable"

        def parser(url:str) -> dict:

            units = ["Batedor", "Cavalaria leve", "Arqueiro a cavalo", "Cavalaria Pesada"]

            soup = BeautifulSoup(url, 'html.parser')

            try:
                orders = []
                # find executing order
                timer = soup.find(id = "trainqueue_wrap_stable")
                timer = list(timer.find_all(attrs = {"class": "lit-item"}))

                queue = soup.find(id = "trainqueue_wrap_stable").find(class_ = "lit-item").text
                for unit in units:
                    if unit in queue:
                        quantity = [int(s) for s in queue.split() if s.isdigit()][0]
                        orders.append({unit:{"duration": timer[1].text, "date_completion": timer[2].text, "quantity": quantity}})

                # find other orders           
                queue = soup.find(id = "trainqueue_stable")

                queue = list(queue.find_all(attrs = {"class": "sortable_row"}))
                for element in queue:
                    lista = (list(element.find_all("td")))
                    for unit in units:
                        if unit in element.text:
                            quantity = [int(s) for s in element.text.split() if s.isdigit()][0]
                            orders.append({unit: {"duration": lista[1].text, "date_completion": lista[2].text, "quantity": quantity}})

                return (orders)

            except AttributeError:
                
                return([]) # return empty list if not training any unit

        with self.session as ses:

            res = ses.get(url)
            return parser(res.text) # done

    def barracks_queue(self, village_id: str) -> dict:

        """ returns list of orders; each order is a dictionary
            [{'Lanceiro': {'duration': '1:06:01', 'date_completion': 'hoje às 15:06:26 horas', 'quantity': 50}}, 
             {'Arqueiro': {'duration': '1:56:30', 'date_completion': 'hoje às 17:02:56 horas', 'quantity': 50}}]
        """

        def parser(url:str) -> dict:

            units = ["Lanceiro", "Espadachim", "Viking", "Arqueiro"  ]

            soup = BeautifulSoup(url, 'html.parser')

            try:
                orders = []
                # find executing order
                timer = soup.find(id = "trainqueue_wrap_barracks")
                timer = list(timer.find_all(attrs = {"class": "lit-item"}))

                queue = soup.find(id = "trainqueue_wrap_barracks").find(class_ = "lit-item").text
                for unit in units:
                    if unit in queue:
                        quantity = [int(s) for s in queue.split() if s.isdigit()][0]
                        orders.append({unit:{"duration": timer[1].text, "date_completion": timer[2].text, "quantity": quantity}})

                # find other orders           
                queue = soup.find(id = "trainqueue_barracks")

                queue = list(queue.find_all(attrs = {"class": "sortable_row"}))
                for element in queue:
                    lista = (list(element.find_all("td")))
                    for unit in units:
                        if unit in element.text:
                            quantity = [int(s) for s in element.text.split() if s.isdigit()][0]
                            orders.append({unit: {"duration": lista[1].text, "date_completion": lista[2].text, "quantity": quantity}})

                return (orders)

            except AttributeError:
                
                return([]) # return empty list if not training any unit




        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=barracks&spear=0&sword=0&axe=0&archer=0&_partial"   
            
        with self.session as ses:

                res = ses.get(url).json()["content"]
                return(parser(res)) # done
    
    def construction_queue(self, village_id: str) -> dict:

        # TODO: add the time till completion of the queued buildings

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
                return(parser(res)) # can be improved 

    def merchant_status(self, village_id:str) -> dict:

        # TODO: add timers of when new merchants will be available

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


    ##################              VILLAGE ORDERS ENDPOINT             ################## 

    # missing research unit
    # train is deprecated

    
    def build(self, village_id: str, building: str ) -> None:
        
        # accessing class property      
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main&ajaxaction=upgrade_building&type=main&h={csrf_token}&&client_time={int(time.time())}"
        body =   f"id={building}&force=1&destroy=0&source=5854"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                action_log("Build order sent successful!") # done

    def train(self, village_id: str, view: str, unit:str, amount: str) -> None:
        
        """ units = [spear, sword, axe, archer -> barracks
                     spy, light, marcher, heavy -> stable
                     ram, catapult -> workshop
                     knight -> statue
                     snob -> snob
                     militia -> farm] """
       
        csrf_token = self.csrf_token
        
        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=stable&ajaxaction=train&mode=train&h={csrf_token}&&client_time={int(time.time())}"
        body = f"units%5B{unit}%5D={amount}"
        
        # send request
        with self.session as ses:
            res = ses.post(base_url, data=body, allow_redirects=False)

            if res.status_code == 200:
                action_log("Train order sent successful!")

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
        target = coord_format(target_village)
        

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
                action_log(f"Attack order sent successful! from: {village_id} to: {target} units: {units}") # done

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
                action_log("Market order created successfully! from: {village_id} {res_sell}: {sell} {res_buy}: {buy} offers: {offers}") # done

    def send_resources(self, village_id:str, target_village: dict, wood: str = 0, stone: str = 0, iron: str = 0):

        """ village_id -> from village id
            target_village ->  {"x": x, "y":y}
            wood -> wood quantity
            stone -> stone quantity
            iron -> iron quantity """

        x = target_village.get("x")
        y = target_village.get("y")
        csrf_token = self._csrf_token

        def coord_format(target_village:dict):

            """ format coordinates -> 123|123 """

            return (f"{x}|{y}")

        base_url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&mode=send&try=confirm_send"
        body = f"wood={wood}&stone={stone}&iron={iron}&x={x}&y={y}&target_type=coord&input="
        target = coord_format(target_village)
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
                action_log("Resources sent successfully! from: {village_id} to: target_village wood: {wood} stone: {stone} iron: {iron}") # done
