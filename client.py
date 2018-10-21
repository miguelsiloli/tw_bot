# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 23:05:28 2018

@author: Geral
"""

import requests
import time

class client():
    
    def __init__(self):
        self.session = requests.Session()
    
    def get(self, url: str, wait: float = 0.5) -> requests.models.Response:    
        time.sleep(wait)
        return(self.session.get(url))
    
    def post(self, url: str, payload: dict = None, json = None, wait: float = 0.5, **kwargs) -> requests.models.Response:        
        time.sleep(wait)
        return(self.session.post(url, data = payload, json = json, **kwargs))
