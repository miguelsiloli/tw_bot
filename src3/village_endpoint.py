# std lib dependancies
import time

# file dependencies
from session import Session
from api_exceptions import SessionException

# module dependencies
from bs4 import BeautifulSoup

# TODO: move parser functions to a seperate module

class Village_Endpoint:
    """This class has methods which contain relevant village information.
       :method troops_available: returns the troops available for actions
       :type: dict
       :method village_info: returns general information of the village
       :type: dict
       :method garage_queue: returns information about workshop queues
       :type: list of dict
       :method stable_queue: returns information about stable queues
       :type: list of dict
       :method barracks_queue: returns information about barracks queues
       :type: list of dict
       :method construction_queue: returns current building name and its timer
       plus list with all the building orders
       :type: list
       :method merchant_status: returns total merchants and available merchants
       :type: dict
	   :method population: returns population and total population
	   :type: dict
       :method command: returns all existing comands
       :type: dict

       note::TODO:
       add smithy information endpoint
       add troops attack power
       add troops defense power
       add troops away
       add troops in village but not from village
    """

    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    _instance = Session("username", "password", "ptxx")

    def __init__(self):

        if Village_Endpoint._instance.verify_session():
            self.session = Village_Endpoint._instance.get_session()
        else:
            self.session = Village_Endpoint._instance.new_session()

        self.gameworld = Village_Endpoint._instance.gameworld
        self.village_id = Village_Endpoint._instance.village_id
        self.csrf_token = Village_Endpoint._instance.csrf_token
        self.session_id = Village_Endpoint._instance.session_id
        self.time = time.time()

    def troops_available(self, village_id:str) -> dict:
        """:returns:
            {
              'available': {
                'spear': '0',
                'sword': '0',
                'axe': '0',
                'archer': '0',
                'spy': '10',
                'light': '4',
                'marcher': '0',
                'heavy': '0',
                'ram': '0',
                'catapult': '0',
                'knight': '1',
                'snob': '0',
                'militia': '0'
              },
              'outgoing': {
                'spear': 0,
                'sword': 0,
                'axe': 0,
                'archer': 0,
                'spy': 0,
                'light': 15,
                'marcher': 0,
                'heavy': 0,
                'ram': 0,
                'catapult': 0,
                'knight': 0,
                'snob': 0,
                'militia': 0
              }
            }
        """
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=place&mode=units"
        unit_list = ["spear", "sword", "axe", "archer", "spy", "light", "marcher", "heavy", "ram", "catapult", "knight", "snob", "militia"]
        troops = {}
        def parser(url:str):
            units = {}
            soup = BeautifulSoup(url, 'html.parser')
            village = soup.find(class_ = "unit-item-spear").find_parent("tr")
            village = list(village.find_all(class_ = "unit-item"))
            count = 0
            for element in village:
                units.update({unit_list[count]: element.text})
                count += 1
            troops.update({"available": units})

            try:
                units = {}
                table = soup.find(attrs = {"id": "units_transit"})
                elements = table.find_all(class_ = "unit-item")
                for unit in unit_list:
                    count = 0
                    for element in elements:
                        if unit in element["class"][1]:
                            count += int(element.text)
                    units.update({unit: count})
                troops.update({"outgoing": units})

            except Exception as e:
                units = {'spear': '0', 'sword': '0', 'axe': '0', 'archer': '0', 'spy': '0', 'light': '0', 'marcher': '0', 'heavy': '0', 'ram': '0', 'catapult': '0', 'knight': '0', 'snob': '0', 'militia': '0'}
                troops.update({"outgoing": units})

            return troops

        with self.session as ses:
            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return parser(res.text)

    def village_info(self, village_id: str) -> dict:
        """ :returns:
            {
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
            } 
            
            :param village_id:
        """
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=api&ajax=resources_schedule&id={village_id}&client_time={self.time}"

        with self.session as ses:

            res  = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(res.json()["game_data"]['village']) # good

    def garage_queue(self, village_id:str) -> dict: # done
        """ :returns: [{'Catapulta': {'duration': '4:58:55', 'date_completion': 'amanhã às 03:01:27 horas', 'quantity': 10}}]

            :param village_id:
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

                return (orders)

            except AttributeError:
                
                return([]) # return empty list if not training any unit

            except Exception: # for unknown exceptions and other exceptions such as unit not being researched or building not built
                # add log
                return([])

        with self.session as ses:

            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return parser(res.text) 

    def stable_queue(self, village_id:str) -> dict:
        """ :returns: [{'Cavalaria leve': {'duration': '0:39:05', 'date_completion': 'hoje às 16:50:10 horas', 'quantity': 13}}]

            :param village_id:
        """         
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
                return([]) 

            except Exception:
                return([])


        with self.session as ses:
            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return parser(res.text) 

    def barracks_queue(self, village_id: str) -> dict: 
        """ :returns: [{'Viking': {'duration': '0:33:34', 'date_completion': 'hoje às 16:40:46 horas', 'quantity': 20}}]

            :param village_id: 
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
                return([]) 

            except Exception: 
                return([])

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=barracks&spear=0&sword=0&axe=0&archer=0&_partial"   
            
        with self.session as ses:
            res = ses.get(url)
            if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return (parser(res.json()["content"]))

    def construction_queue(self, village_id: str) -> dict:        
        """ :returns: {'Est�bulo': '3:21:29'} ['Est�bulo', 'Mercado', 'Mercado', 'Mercado', 'Fazenda']

            :param village_id:
        """
        # TODO: add the time till completion of the queued buildings
        def parser(url:str) -> dict:

            """ format: buildings = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main" 
                returns the executing training queue and the name of the queued buildings 
            """

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
                        element = ele.text
                        for count in range(len(buildings_list)):
                            if buildings_list[count] in element:  
                                queue.append(buildings_list[count])
                                if not construction_queue: # make sure you just get the first building                       
                                    construction_queue = {buildings_list[count]: timer.text}

                return(construction_queue, queue)

            except AttributeError:                
                return ({})

            except Exception:
                return([]) 
            
        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=main"
            
        with self.session as ses:
            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(parser(res.text)) # can be improved 

    def merchant_status(self, village_id:str) -> dict:      
        """ :returns: {'merchant_available': '83', 'merchant_total': '110'}
            
            :param village_id:
        """

        def parser(url:str) -> dict:
            soup = BeautifulSoup(url, 'html.parser')
            merchant_available = soup.find(id = "market_merchant_available_count").text
            merchant_total = soup.find(id = "market_merchant_total_count").text
            return({"merchant_available": merchant_available, "merchant_total": merchant_total})

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&mode=traders"

        with self.session as ses:

            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(parser(res.text)) # okay

    def commands(self, village_id: str) -> dict:
        """:returns:
           [{'type': 'return', 'target': '523|445', 'continent': '45', 'duration': '0:05:40', 'date_completion': 'hoje às 12:52:00:000 horas'}, {'type': 'return', 'target': '508|436', 'continent': '45', 'duration': '0:08:17', 'date_completion': 'hoje às 12:54:37:000 horas'}]

           :param: village_id
        """

        def parser(url:str) -> dict:
            soup = BeautifulSoup(url, 'html.parser') 
            command_list = []
            try:
                outgoing = soup.find(class_ = "commands-container")
                commands = outgoing.find_all(class_ = "command-row")               
                for command in commands:
                    type = command.find(class_ = "command_hover_details")["data-command-type"]
                    _coord = [str(s) for s in command.find("a").text.strip("\n").strip(" ") if s.isdigit()]
                    _len = len(_coord)
                    _coord = _coord[(_len-8):_len]
                    target = "".join(_coord[:3]) + "|" + "".join(_coord[3:6])
                    continent = "".join(_coord[6:8])
                    timer = command.find(class_ = "widget-command-timer").text
                    date = command.find_all("td")[1].text
                    command_list.append({"type": type, "target": target, "continent": continent, "duration": timer, "date_completion": date})

            except AttributeError:
                pass

            return soup

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview"

        with self.session as ses:

            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(parser(res.text)) # okay

    def premium_stock(self, village_id):
        """:returns:
        {
          'response': {
            'stock': {
              'wood': 195479,
              'stone': 203267,
              'iron': 206000
            },
            'capacity': {
              'wood': 217302,
              'stone': 216307,
              'iron': 214073
            },
            'rates': {
              'wood': 0.002808407852,
              'stone': 0.002269308146,
              'iron': 0.001975003525
            },
            'tax': {
              'buy': 0.03,
              'sell': 0
            },
            'constants': {
              'resource_base_price': 0.015,
              'resource_price_elasticity': 0.0148,
              'stock_size_modifier': 20000
            },
            'duration': 3600,
            'merchants': 39,
        }
        """

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=market&ajax=exchange_data&client_time={self.time}"

        with self.session as ses:

            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return(res.json()) # okay


#print(Village_Endpoint().premium_stock("4284"))
#print(Village_Endpoint().troops_available("4284"))
#print(Village_Endpoint().commands("4284"))
#print(Village_Endpoint().village_info("40568"))
#print(Village_Endpoint().garage_queue("25382"))
#print(Village_Endpoint().stable_queue("25382"))
#print(Village_Endpoint().barracks_queue("25382"))
#print(Village_Endpoint().construction_queue("25382"))
#print(Village_Endpoint().merchant_status("25382"))
#print(Village_Endpoint().population("25382"))

