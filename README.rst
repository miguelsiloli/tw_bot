.. image:: https://dspt.innogamescdn.com/asset/4d47dbcf/graphic/start2/bg-paladin.png
   :height: 150px
   :target: https://www.tribalwars.com.pt/
   
TribalWars Scrapper
===================

TribalWars (TW) scrapper is a high level fast web crawling API built on Requests and BeautifulSoup used to extract structured data (JSON format) and crawl TW pages. It can be used for a wide range of purposes, including simulating web-browser actions undetected, insert and plan custom commands, data mining with the market database, world data and reports analyzes (WIP)

Classes
=======

* Client: modified requests.Requets class to throttle the number of requets and avoid bot detection
* Session: session handler singleton which insures the class has only one instance. Each session has a specific crsf_token and session_id cookies and terminates the previous session. Helpful with concurrency.
* User Endpoint (Extends Session): contains get methods for user data
* Actions Endpoint (Extends Session): contains post methods for village_id
* Village Endpoint (Extends Session): contains get methods for village_id
* World: contains get methods for public accessible data. Helpful to monitor user, ally, village activity by tracking attack/defense stats, village/user/ally points, etc

.. image:: https://github.com/lmao420blazeit/tw_bot/blob/master/img/classes.png
   :alt: Alternative text

Requirements
============

* Python 3.7+
* Works on Linux, Windows, macOS, BSD
