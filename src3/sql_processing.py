import pandas as pd
from market_bot import Database

class Market_AI(Database):

    def read_sql(self):
        conn = self.connection
        query = "SELECT time, ratio_wood, ratio_ston, ratio_iron FROM Market"
        resp = pd.read_sql_query(query, conn)
        conn.close()
        return(resp)

Market_AI().read_sql()