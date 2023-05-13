#!/usr/bin/env python3
import pandas as pd
import requests

from cache import Cache

def getLocation(src):
  response = requests.get(f'https://dazzlepod.com/ip/{src}.json')
  json = response.json()
  return [json.get(key, None) for key in ['country', 'city', 'latitude', 'longitude']] # TODO: Handle error

def getBestSrc(data):
  df = pd.DataFrame(data)

  if len(data) == 0:
    return {'src': None, 'rtt': None, 'country': None, 'city': None, 'lat': None, 'long': None}

  src = df['src'].mode().iloc[0]
  mean = df[df['src'] == src]['rtt'].mean()
  country, city, lat, long = getLocation(src)

  return {'src': src, 'rtt': mean, 'country': country, 'city': city, 'lat': lat, 'long': long}

def process(cache):
  dfName = 'df' # TODO: Better name
  df = cache.loadDf(dfName)
  if df is not None:
    return df

  _, hostData = cache.loadPickle()

  df = pd.DataFrame([
    getBestSrc(data)
    for data in hostData
  ])

  df.dropna(subset=['src'], inplace = True) # TODO: Do something with missing hops

  cache.saveDf(df, dfName)
  return df
