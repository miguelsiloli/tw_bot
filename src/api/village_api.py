# std lib dependancies
import logging
import time

# file dependencies
from session import Session
from tw_log import action_log
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

    _instance = Session("Seelfed", "azulcaneta7", "pt62")

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
                
                return([]) # return empty list if not training any unit

            except Exception: # for unknown exceptions and other exceptions such as unit not being researched or building not built
                # add log
                return([])


        with self.session as ses:
            res = ses.get(url)
            if res == "https://www.tribalwars.com.pt/?session_expired=1":
                raise SessionException

        return parser(res.text) 

    def barracks_queue(self, village_id: str) -> dict: # error when queue is empty
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
                
                return([]) # return empty list if not training any unit

            except Exception: # for unknown exceptions and other exceptions such as unit not being researched or building not built
                # add log
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
                        element = ele.text #building name #.find(class_="order-progress")
                        for count in range(len(buildings_list)):
                            if buildings_list[count] in element:  
                                queue.append(buildings_list[count])
                                if not construction_queue: # make sure you just get the first building                       
                                    construction_queue = {buildings_list[count]: timer.text}

                return(construction_queue, queue)

            except AttributeError:
                
                return ({})

            except Exception:
                # add log
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

    def population(self, village_id: str) -> dict:
        """ :returns: {'pop': '16904', 'max_pop': '26400'}

            :param village_id:
        """

        def parser(url:str):
            soup = BeautifulSoup(url, 'html.parser')
            pop = soup.find(attrs={"id": "pop_current_label"}).text
            pop_max = soup.find(attrs={"id": "pop_max_label"}).text
            return({"pop": pop, "max_pop": pop_max})

        url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=overview"

        with self.session as ses:

                res = ses.get(url)
                if res == "https://www.tribalwars.com.pt/?session_expired=1":
                    raise SessionException

        return(parser(res.text)) # okay
