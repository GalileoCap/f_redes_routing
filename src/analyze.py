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

def cimbalaMethod(df, column, alpha = 0.05, alt = False):
  key = 'cimbalaAlt_pred' if alt else 'cimbala_pred'

  df[key] = False
  if len(df) < 3:
    log('[cimbalaMethod] Not enough data points', level = 'error')
    return None

  # if not alt:
    # print('deviation', abs(df[column] - df[column].mean()))

  while True:
    _df = df[~df[key]][[column]].copy()
    _df.dropna(subset=[column], inplace = True)
    if len(_df) == 0:
      break

    _df['deviation'] = abs(_df[column] - _df[column].mean())
    maxDeviationIdx = _df['deviation'].idxmax()

    tS = 0
    if alt:
      tS = 0.1 # TODO: Valor de corte fijo
    else:
      tS = thompsonT(_df[column].count(), alpha) * _df[column].std()

    if _df.at[maxDeviationIdx, 'deviation'] > tS: # Is an outlier
      df.at[maxDeviationIdx, key] = True
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
  graphMethod(df)
  cimbalaMethod(df, 'drtt')
  cimbalaMethod(df, 'drtt', alt = True)

  # cache.saveDf(df, dfName) # TODO: Uncomment once done
  return df
  
def report(cache):
  df = analyze(cache)
  print(df[['src', 'country', 'rtt', 'drtt', 'naive_pred', 'graph_pred', 'cimbala_pred', 'cimbalaAlt_pred']], sep = '\n')

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
