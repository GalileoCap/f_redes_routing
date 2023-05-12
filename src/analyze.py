#!/usr/bin/env python3
import sys
import pandas as pd
# import numpy as np
import requests

from cache import Cache
import utils
from utils import log

def getLocation(src):
  response = requests.get(f'https://dazzlepod.com/ip/{src}.json')
  json = response.json()
  return [json.get(key, None) for key in ['country', 'city', 'latitude', 'longitude']] # TODO: Handle error

def getBestSrc(data):
  df = pd.DataFrame(data)

  src = df['src'].mode().iloc[0]
  mean = df[df['src'] == src]['rtt'].mean()
  country, city, lat, long = getLocation(src)

  return {'src': src, 'rtt': mean, 'country': country, 'city': city, 'lat': lat, 'long': long}

def analyzeHost(host, hostData, success, info, cache):
  dfName = host # TODO: Better name
  df = cache.loadDf(dfName)
  if df is not None:
    return df

  df = pd.DataFrame([
    getBestSrc(data)
    for data in hostData
  ])

  df['drtt'] = df['rtt'].diff() # TODO: Negative deltas

  cache.saveDf(df, dfName)
  return df

def analyze(info, data, cache): # TODO: Rename
  log(f'[analyze] fbase={cache.fbase}', level = 'user')
  for host, (hostData, success) in data.items():
    print(host, analyzeHost(host, hostData, success, info, cache), sep = '\n')

def analyzeFile(fbase, save = True, load = True):
  cache = Cache(fbase, save, load)

  info, data = utils.loadPickle(fbase) # TODO: Use Cache
  analyze(info, data, cache)

if __name__ == '__main__':
  files = sys.argv[1:] if len(sys.argv) >= 2 else utils.getAllDataFiles()

  for fpath in files:
    try: # TODO: Shouldn't fail, fix analyzeHost
      analyzeFile(fpath[:-4]) # Remove .pkl
    except:
      log('[analyze.MAIN] {fpath}', level = 'error')
