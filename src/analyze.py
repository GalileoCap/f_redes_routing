#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
import scipy.stats as sps
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

  df = df[df['src'] != None] # TODO: Do something with missing hops

  cache.saveDf(df, dfName)
  return df

def thompson(n):
  return ()

def analyze(info, data, cache): # TODO: Rename
  log(f'[analyze] fbase={cache.fbase}', level = 'user')
  for host, (hostData, success) in data.items():
    df = analyzeHost(host, hostData, success, info, cache)

    df['drtt'] = df['rtt'].diff()
    df['dlat'] = df['lat'].diff()
    df['dlong'] = df['long'].dggiff()
    df['distance'] = np.sqrt(df['dlat'] ** 2 + df['dlong'] ** 2)

    df['our_predicted'] = df['drtt'] >= 0.01

    # mean = df['drtt'].mean()
    # t = thompson(df['drtt'].count())
    df['cimbala_predicted'] = False

    print(host, df[['src', 'country', 'rtt', 'drtt', 'our_predicted', 'cimbala_predicted']], sep = '\n')

def analyzeFile(fbase, save = True, load = True):
  cache = Cache(fbase, save, load)

  info, data = utils.loadPickle(fbase) # TODO: Use Cache
  analyze(info, data, cache)

if __name__ == '__main__':
  pass
if False:
  files = sys.argv[1:] if len(sys.argv) >= 2 else utils.getAllDataFiles()

  for fpath in files:
    analyzeFile(fpath[:-4]) # Remove .pkl
