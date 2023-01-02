import logging
import os
import random

import newrelic.agent
import pandas as pd
import pymongo


@newrelic.agent.background_task()
def get_client():
    client = pymongo.MongoClient(
        os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
        readPreference='secondaryPreferred',
        appname='petrosa-nosql-crypto'
    )
    
    return client



@newrelic.agent.background_task()
def get_data(ticker, period, limit=999999999):

    if(period == '5m'):
        suffix = 'm5'
    elif(period == '15m'):
        suffix = 'm15'
    elif(period == '30m'):
        suffix = 'm30'
    elif(period == '1h'):
        suffix = 'h1'
    else:
        suffix = ''

    client = get_client()
    db = client["petrosa_crypto"]
    history = db["candles_" + suffix]

    results = history.find({'ticker': ticker},
                           sort=[('datetime', -1)]).limit(limit)
    results_list = list(results)

    if (len(results_list) == 0):
        return []

    data_df = pd.DataFrame(results_list)

    data_df = data_df.sort_values("datetime")

    data_df = data_df.rename(columns={"open": "Open",
                                      "high": "High",
                                      "low": "Low",
                                      "close": "Close"}
                             )

    data_df = data_df.set_index('datetime')

    return data_df


@newrelic.agent.background_task()
def find_params():
    client = get_client()
    try:
        params = client.petrosa_crypto['backtest_controller'].find(
            {"status": 0, "strategy": "simple_gap_finder"})
        params = list(params)

        if len(params) == 0:
            params = client.petrosa_crypto['backtest_controller'].find(
                {"status": 1, "strategy": "simple_gap_finder"})
            params = list(params)

        if len(params) == 0:
            params = client.petrosa_crypto['backtest_controller'].find(
                {"strategy": "simple_gap_finder"})
            params = list(params)

        if len(params) == 1:
            params = params[0]
        elif len(params) == 0:
            raise Exception("No params found, check DB")
        else:
            params = params[random.randint(0, len(params))]
            
        client.petrosa_crypto['backtest_controller'].update_one(
            params, {"$set": {"status": 1}})
    except Exception as e:
        logging.error(e)
        raise
            

    return params


@newrelic.agent.background_task()
def update_status(params, status):
    client = get_client()

    client.petrosa_crypto['backtest_controller'].update_one(
        {"_id": params['_id']}, {"$set": {"status": status}})
    
    return True


@newrelic.agent.background_task()
def post_results(symbol, test_period, doc):
    client = get_client()

    client.petrosa_crypto['backtest_results'].update_one(
                                                {"strategy": "simple_gap_finder",
                                                "symbol": symbol,
                                                "period": test_period
                                                }, {"$set": doc}, upsert=True)
    return True
