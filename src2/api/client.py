import requests
import time
from random import randint

class client():
    """Modified requests.Requests class.
       :method get: REST GET 
       :method post: REST POST
    """
    
    def __init__(self):
        self.session = requests.Session()
    
    def get(self, url: str, wait: float = randint(3, 5), timeout: float = 5, **kwargs) -> requests.models.Response:    
        """ :returns: requests.models.Response
            
            :param url: base url
            :param wait: time elapsed between each call
            :param timeout: response timeout

            note::wait param prevents captchas
        """
        time.sleep(wait)
        return(self.session.get(url, timeout, **kwargs))
    
    def post(self, url: str, payload: dict = None, json = None, wait: float = randint(3, 5), timeout: float = 5, **kwargs) -> requests.models.Response:  
        """ :returns: requests.models.Response
            
            :param url: base url
            :param payload: body to transport in request
            :param wait: time elapsed between each call
            :param timeout: response timeout

            note::wait param prevents captchas
        """
        time.sleep(wait)
        return(self.session.post(url, data = payload, json = json, **kwargs))