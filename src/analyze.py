#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np
from scipy import stats

from cache import Cache
from process import process
import utils
from utils import log

#############################################################
# S: Our naive method #######################################

def naiveMethod(df):
  df['naive_pred'] = df['drtt'] >= 0.1

#############################################################
# S: Cimbala's method #######################################
# SEE: https://www.me.psu.edu/cimbala/me345/Lectures/Outliers.pdf

def thompsonT(n, alpha = 0.05):
  t = stats.t.ppf(1 - alpha/2, n - 2)
  return (t * (n - 1)) / (np.sqrt(n) * np.sqrt(n - 2 + t**2))

def cimbalaMethod(df, alpha = 0.05):
  df['cimbala_pred'] = False
  if len(df) < 3:
    log('[cimbalaMethod] Not enough data points', level = 'error')
    return None

  while True:
    _df = df[~df['cimbala_pred']][['drtt']].copy()
    _df.dropna(subset=['drtt'], inplace = True)
    if len(_df) == 0:
      break

    _df['deviation'] = (_df['drtt'] - _df['drtt'].mean())
    maxDeviationIdx = _df['deviation'].idxmax()

    tS = thompsonT(df['drtt'].count(), alpha) * _df['drtt'].std()
    print(_df.at[maxDeviationIdx, 'deviation'], tS)
    if _df.at[maxDeviationIdx, 'deviation'] > tS: # Is an outlier
      df.at[maxDeviationIdx, 'cimbala_pred'] = True
    else: # There are no more outliers
      break

def graphMethod(df):
  df['graph_pred'] = False

def analyze(cache):
  dfName = 'dfA' # TODO: Better name
  df = cache.loadDf(dfName)
  if df is not None:
    return df

  log(f'[analyze] fbase={cache.fbase}', level = 'user')
  df = process(cache)

  df.dropna(subset=['src', 'rtt'], inplace = True)

  df['drtt'] = df['rtt'].diff()
  # while df['drtt'].min() < 0:
    # df = df[df['drtt'] > 0]
    # df['drtt'] = df['rtt'].diff()

  df['dlat'] = df['lat'].diff()
  df['dlong'] = df['long'].diff()
  df['distance'] = np.sqrt(df['dlat'] ** 2 + df['dlong'] ** 2)

  naiveMethod(df)
  cimbalaMethod(df)
  graphMethod(df)

  # cache.saveDf(df, dfName) # TODO: Uncomment once done
  return df
  
def report(cache):
  df = analyze(cache)
  print(df[['src', 'country', 'rtt', 'drtt', 'naive_pred', 'cimbala_pred', 'graph_pred']], sep = '\n')

if __name__ == '__main__':
  files = sys.argv[1:] if len(sys.argv) >= 2 else utils.getAllDataFiles()
  save = True
  load = True

  for fpath in files:
    fbase = fpath[:-4] # Remove .pkl
    cache = Cache(fbase, save, load)
    if cache.loadPickle() is None:
      log('[analyzeCase] No pickle for {fbase}', level = 'error')
    else:
      report(cache)
