# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 12:08:15 2018

@author: Geral
"""
import json

class tw_api_exception(Exception):
    
    def __ini__(self, response):
        self.code = ""
        self.message = "Unknown Error"
        self.url = ""
        self.request = ""
        self.error = ""
        
        try:
            self.code = response.status_code 
            self.url = response.url
            self.request = response.request
            self.error = response.raise_for_status()
            
        except ValueError:
            self.message = response.content
            
        finally:
            self.message = response.text

            
    
    def __str__(self):
        return json.dumps({"status code": self.code,
                "error type": self.error,
                "error request": self.request,
                "url": self.url,
                "message": self.message})
