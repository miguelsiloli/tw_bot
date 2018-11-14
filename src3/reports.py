from session import Session
import time
from bs4 import BeautifulSoup

class Reports:

    _status_code = {"200": "OK", 
                    "202": "Created",
                    "204": "Accepted", 
                    "400": "Bad Request", 
                    "500": "Internal Server Error"}

    _instance = Session("Vanisher", "azulcaneta7", "pt64")

    def __init__(self):

        if Reports._instance.verify_session():
            self.session = Reports._instance.get_session()
        else:
            self.session = Reports._instance.new_session()

        self.gameworld = Reports._instance.gameworld
        self.village_id = Reports._instance.village_id
        self.csrf_token = Reports._instance.csrf_token
        self.session_id = Reports._instance.session_id
        self.time = time.time()


    def attack(self, village_id: str, name_lookup: str, date_lookup: str):
        """:returns:
                [
          {
            'name': 'Vanisher (Aldeia de Papitips420) ataca Aldeia de talhante1 (517|433) K45',
            'date': 'nov 13, 10:20',
            'href': '/game.php?village=4284&screen=report&mode=attack&group_id=0&view=985626',
            'from_id': '4284',
            'target_coord': '517|433',
            'tags': [
              'Pequeno ataque (1-1000 tropas)',
              'Com batedores',
              'Vitoria total',
            ]
          },
          {
            'name': 'Vanisher (Aldeia de Papitips420) ataca Aldeia de voti123 (518|436) K45',
            'date': 'nov 13, 10:07',
            'href': '/game.php?village=4284&screen=report&mode=attack&group_id=0&view=983821',
            'from_id': '4284',
            'target_coord': '518|436',
            'tags': [
              'Pequeno ataque (1-1000 tropas)',
              'Com batedores',
              'Vitoria total',
            ]
          }
        ]

           :param village_id:
           :param name_lookup: last report name
           :param date_lookup: last report date
        """
        global found_flag
        found_flag = False
        report = []

        def retrieve_coord(text: str):
            _coord = [str(s) for s in text if s.isdigit()]
            _len = len(_coord)
            _coord = _coord[(_len-8):_len]
            target_coord = "".join(_coord[:3]) + "|" + "".join(_coord[3:6])
            return target_coord

        def parser(url: str):
            soup  = BeautifulSoup(url, 'html.parser')
            table = soup.find("table", attrs = {"id": "report_list"})
            tr_list = table.find_all("tr")          
            for tr in tr_list:
                try:
                    div = tr.find_all("div", class_ = "nowrap float_right" )
                    for _div in div:
                        report_tags = []
                        td = tr.find_all("td")[1]
                        tag_list = td.findChildren("img")
                        for tag in tag_list:
                            report_tags.append(tag["title"])

                        date = tr.find("td", class_ = "nowrap").text
                        link = tr.find_all("td")[1].find("a")["href"]
                        name = " ".join(tr.find_all("td")[1].find("a").text.split())                 
                        from_id = village_id
                        target_coord = retrieve_coord(name)
                        if name == name_lookup and date == date_lookup:
                            global found_flag
                            found_flag = True                            
                            return report
                        else:
                            report.append({"name": name, "date": date, "href": link, "from_id": from_id, "target_coord": target_coord, "tags": report_tags})

                except Exception as e:
                    print (e)

            return []
        
        def request(url: str):

            with self.session as ses:

                res  = ses.get(url)
                if res.url == "https://www.tribalwars.com.pt/?session_expired=1":
                    raise SessionException
                else:
                    return parser(res.text)

        page_list = ["0", "12", "24", "48"]
        for page in page_list:           
            url = f"https://{self.gameworld}.tribalwars.com.pt/game.php?village={village_id}&screen=report&mode=attack&from={page}&group_id=0"
            reports = []
            reports.append(request(url))
            if found_flag == True:
                return (reports)

        return []


#print(Reports().attack("4284", "Vanisher (Aldeia de Papitips420) ataca -GooD MorNinG (516|442) K45", "nov 13, 16:35"))
#https://pt64.tribalwars.com.pt/game.php?village=4284&screen=report&mode=all&group_id=0
#https://pt64.tribalwars.com.pt/game.php?village=4284&screen=report&mode=all&group_id=13317
