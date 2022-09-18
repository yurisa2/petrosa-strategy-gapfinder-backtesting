import pymongo
import os


client = pymongo.MongoClient(
            os.getenv(
                'MONGO_URI', 'mongodb://root:wUx3uQRBC8@localhost:27017'),
            readPreference='secondaryPreferred',
            appname='petrosa-nosql-crypto'
                                    )



col_symbols = client.petrosa_crypto['candles_h1'].aggregate(
    [{
    "$group" :
        {"_id" : "$ticker"
         }}
    ])


periods = ['5m', '15m', '30m', '1h']


full_bt_list = []

for symbol in col_symbols:
    for period in periods:
        row = {}
        row['symbol'] = symbol['_id']
        row['period'] = period
