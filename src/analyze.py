#!/usr/bin/env python3
import sys
import pandas as pd
import networkx as nx
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

Nodes = {}
Edges = {}

def addToGraph(df):
  def row2Edge(row):
    u = row['src']
    Nodes[u] = Nodes.get(u, []) + [{
      'country': row['country'],
      'lat': row['lat'],
      'long': row['long'],
    }]

    v = row['prev']
    if v is not None: # First node is the source and has no prev
      Edges[(v, u)] = Edges.get((v, u), []) + [{
        'rtt': row['drtt'],
        'length': row['distance'],
        'naive_pred': row['naive_pred'],
        'cimbala_pred': row['cimbala_pred'],
        'cimbalaAlt_pred': row['cimbalaAlt_pred'],
      }]

  df['prev'] = df['src'].shift(1)
  df['idx'] = df.index # Hack to use index in row2Edge
  df.apply(row2Edge, axis = 'columns')
  df.drop('idx', axis = 'columns', inplace = True)

def analyze(cache):
  dfName = 'dfA' # TODO: Better name
  df = cache.loadDf(dfName)
  if df is not None:
    return df

  log(f'[analyze] fbase={cache.fbase}', level = 'user')
  df = process(cache)

  df.dropna(subset=['src', 'rtt'], inplace = True)

  df['drtt'] = df['rtt'].diff()
  # df.drop(df[df['drtt'] > 0].index, inplace = True)
  # while df['drtt'].min() < 0:
    # df.drop(df[df['drtt'] > 0].index, inplace = True)
    # df['drtt'] = df['rtt'].diff()

  df['dlat'] = df['lat'].diff()
  df['dlong'] = df['long'].diff()
  df['distance'] = np.sqrt(df['dlat'] ** 2 + df['dlong'] ** 2)

  naiveMethod(df)
  cimbalaMethod(df, 'drtt')
  cimbalaMethod(df, 'drtt', alt = True)

  addToGraph(df)

  # cache.saveDf(df, dfName) # TODO: Uncomment once done
  return df
  
def report(cache):
  df = analyze(cache)
  print(df[['src', 'country', 'rtt', 'drtt', 'naive_pred', 'cimbala_pred', 'cimbalaAlt_pred']], sep = '\n')

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

  # TODO: Save graphData
  G = nx.Graph()
  for v, data in Nodes.items():
    G.add_node(v, count = len(data), **data[0]) # TODO: Check no differences in location labeling

  for e, data in Edges.items():
    rtt = np.mean([dataPoint['rtt'] for dataPoint in data])
    length = data[0]['length'] # TODO: Check no differences in location labeling
    naive_pred = np.mean([int(dataPoint['naive_pred']) for dataPoint in data])
    cimbala_pred = np.mean([int(dataPoint['cimbala_pred']) for dataPoint in data])
    cimbalaAlt_pred = np.mean([int(dataPoint['cimbalaAlt_pred']) for dataPoint in data])
    G.add_edge(*e, count = len(data), rtt = rtt, length = length, naive_pred = naive_pred, cimbala_pred = cimbala_pred, cimbalaAlt_pred = cimbalaAlt_pred)

  print(G)
  print(G.nodes['200.51.241.1'])
  print(G.edges['192.168.1.1', '200.51.241.1'])
