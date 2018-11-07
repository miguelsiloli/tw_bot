from world_sql import Database

class Query(Database):

    """
    {   
        # select by id

        "select_pdata_by_pid": returns all the player data from Player,
        "select_ally_data_by_pid": returns all the ally data, ,
        "select_pvill_by_pid": returns data from the villages owned by player,
        "select_oda_by_pid": returns data on the ODA,
        "select_odd_by_pid": returns data on the ODD,
        "get_odd": returns data of defensive pontuation of all players alive,
        "get_oda": returns data of offensive pontuation of all players alive,
        "select_players_from_aid": returns data from all the players from player_id ally
    }
    """

    def __init__(self):
        super(Query, self).__init__()

    def _deserialize(self):
        desc = self.cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in self.cursor.fetchall()]
        return data

    ### SELECT BY PLAYER ID ###

    def select_pdata_by_pid(self, player_id:int, limit = 1) -> list:

        """
        [{'player_id': 533, 'name': 'carlos cabrita', 'ally_id': 807, 'num_vill': 3, 'points': 7216, 'rank': 1018, 'datetime': '2018-11-05 12:14:10.266625'}]
        """

        self.cursor.execute(f"SELECT * FROM Player WHERE player_id = {player_id} LIMIT {limit}") 
        return (self._deserialize())

    def select_ally_data_by_pid(self, player_id:int) -> list:

        """
        [{'ally_id': 807, 'name': 'Smile for Death', 'tag': 'SKULL', 'members': 26, 'points': 87995, 'total_points': 87995, 'rank': 39, 'datetime': '2018-11-05 12:14:10.867885'}]
        """

        self.cursor.execute(f"SELECT * FROM Ally WHERE ally_id = (SELECT ally_id FROM Player WHERE player_id = {player_id})") 
        return (self._deserialize())

    def select_pvill_by_pid(self, player_id: int) -> list:

        """
        [(35281, 'Aldeia de carlos cabrita 02', 391, 347, 33, 533, 2540, '2018-11-05'), (40953, 'Aldeia de carlos cabrita 03', 391, 346, 33, 533, 839, '2018-11-05'), (44507, 'Aldeia de carlos cabrita', 393, 345, 33, 533, 3950, '2018-11-05')]
        """

        self.cursor.execute(f"SELECT * FROM Village WHERE player_id = {player_id}") 
        return (self._deserialize())       

    def select_oda_by_pid(self, player_id: int) -> list:

        """
        [(533, 522, 1621, '2018-11-05')]
        """

        self.cursor.execute(f"SELECT * FROM ODA WHERE player_id = {player_id}") 
        return (self._deserialize())

    def select_odd_by_pid(self, player_id: int) -> list:

        """
        [(533, 52212, 1149, '2018-11-05')]
        """

        self.cursor.execute(f"SELECT * FROM ODD WHERE player_id = {player_id}") 
        return (self._deserialize())

    def select_players_from_aid(self, player_id: int) -> list:

        """
        [{'player_id': 533, 'name': 'carlos cabrita', 'ally_id': 807}, {'player_id': 102216, 'name': 'telmorosa', 'ally_id': 807}, {'player_id': 205417, 'name': 'ANIBALL', 'ally_id': 807}, {'player_id': 257275, 'name': 'bloodking', 'ally_id': 807}, {'player_id': 649921, 'name': 'Giannoni', 'ally_id': 807}, {'player_id': 666339, 'name': 'maste2435', 'ally_id': 807}, {'player_id': 1276477, 'name': 'yaradog', 'ally_id': 807}, {'player_id': 1333700, 'name': 'loiroslb', 'ally_id': 807}, {'player_id': 1405860, 'name': 'morfyne', 'ally_id': 807}, {'player_id': 1412200, 'name': 'turra13', 'ally_id': 807}, {'player_id': 1982207, 'name': 'Jr78', 'ally_id': 807}, {'player_id': 2014760, 'name': 'Reiscorpion', 'ally_id': 807}, {'player_id': 2016176, 'name': 'GtailPT', 'ally_id': 807}, {'player_id': 2355222, 'name': 'ivoking', 'ally_id': 807}, {'player_id': 2376951, 'name': 'oldstyle2', 'ally_id': 807}, {'player_id': 2515869, 'name': 'daviki', 'ally_id': 807}, {'player_id': 2718891, 'name': 'Rei Godinho', 'ally_id': 807}, {'player_id': 2740651, 'name': 'zombieboy', 'ally_id': 807}, {'player_id': 2755276, 'name': 'NeonDage', 'ally_id': 807}, {'player_id': 2759909, 'name': 'Rjvt85', 'ally_id': 807}, {'player_id': 3091083, 'name': 'RenatoRocha7', 'ally_id': 807}, {'player_id': 3098952, 'name': 'skorpion81', 'ally_id': 807}, {'player_id': 3100378, 'name': 'lille', 'ally_id': 807}, {'player_id': 3105114, 'name': 'rev77boy', 'ally_id': 807}, {'player_id': 3105314, 'name': 'CarolinaMoura8', 'ally_id': 807}, {'player_id': 3107767, 'name': 'Joaoserpa3345', 'ally_id': 807}]
        """

        self.cursor.execute(f"SELECT DISTINCT player_id, name, ally_id FROM Player WHERE ally_id = (SELECT ally_id FROM Player WHERE player_id = {player_id}) ") 
        return (self._deserialize())




#print(Query().select_oda_by_pid("533"))
print(Query().select_ally_data_by_pid("533"))