import pymongo
import pandas as pd
import os

def get_data(ticker, period, limit=999999999):

    if(period == '5m'):
        suffix = 'm5'
    if(period == '15m'):
        suffix = 'm15'
    if(period == '30m'):
        suffix = 'm30'
    if(period == '1h'):
        suffix = 'h1'


    client = pymongo.MongoClient(
                os.getenv(
                    'MONGO_URI', 'mongodb://root:wUx3uQRBC8@localhost:27017'),
                readPreference='secondaryPreferred',
                appname='petrosa-nosql-crypto'
                                        )
    db = client["petrosa_crypto"]
    history = db["candles_" + suffix]

    results = history.find({'ticker': ticker},
                           sort=[('datetime', -1)]).limit(limit)
    results_list = list(results)

    data_df = pd.DataFrame(results_list)
    data_df = data_df.sort_values("datetime")

    data_df = data_df.rename(columns={"open": "Open",
                                      "high": "High",
                                      "low": "Low",
                                      "close": "Close"}
                                      )


    data_df = data_df.set_index('datetime')

    return data_df
