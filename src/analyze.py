#!/usr/bin/env python3
import sys
import pandas as pd
import networkx as nx
import numpy as np
from scipy import stats

from cache import Cache
from process import process
from plot import worldPlot, graphPlot, droppedPlot
import utils
from utils import log

#############################################################
# S: Our naive method #######################################

def naiveMethod(df, column, cutoff = 0.07):
  df['naive_pred'] = df[column] >= cutoff

#############################################################
# S: Cimbala's method #######################################
# SEE: https://www.me.psu.edu/cimbala/me345/Lectures/Outliers.pdf

def thompsonT(n, alpha = 0.05):
  t = stats.t.ppf(1 - alpha/2, n - 2)
  return (t * (n - 1)) / (np.sqrt(n) * np.sqrt(n - 2 + t**2))

def cimbalaMethod(df, column, alpha = 0.05, altCutoff = None):
  key = 'cimbala_pred' if altCutoff is None else 'cimbalaAlt_pred'

  df[key] = False
  if len(df) < 3:
    log('[cimbalaMethod] Not enough data points', level = 'error')
    return None

  while True:
    _df = df[~df[key]][[column]].copy()
    _df.dropna(subset=[column], inplace = True)
    if len(_df) == 0:
      break

    _df['deviation'] = abs(_df[column] - _df[column].mean())
    maxDeviationIdx = _df['deviation'].idxmax()

    tS = altCutoff
    if tS is None:
      tS = thompsonT(_df[column].count(), alpha) * _df[column].std()

    if _df.at[maxDeviationIdx, 'deviation'] > tS: # Is an outlier
      df.at[maxDeviationIdx, key] = True
    else: # There are no more outliers
      break

#############################################################
# S: Analyze a single route #################################

dropNa = []
dropDrtt = []

def analyzeRoute(cache):
  dfName = 'dfA' # TODO: Better name
  df = cache.loadDf(dfName)
  if df is not None:
    return df

  log(f'[analyze] fbase={cache.fbase}', level = 'deepDebug')
  df = process(cache)

  preDrop = len(df)
  df.dropna(subset=['src', 'rtt'], inplace = True) # TODO: How many were dropped?
  dropped = preDrop - len(df)
  dropNa.append((dropped, dropped / preDrop))

  preDrop = len(df)
  df['drtt'] = df['rtt'].diff()
  df.drop(df[df['drtt'] < 0].index, inplace = True)
  # while df['drtt'].min() < 0:
    # df.drop(df[df['drtt'] < 0].index, inplace = True)
    # df['drtt'] = df['rtt'].diff()
  dropped = preDrop - len(df)
  dropDrtt.append((dropped, dropped / preDrop))

  naiveMethod(df, 'drtt')
  cimbalaMethod(df, 'drtt')
  cimbalaMethod(df, 'drtt', altCutoff = 0.02) # TODO: altCutoff

  addRouteToGraph(df)

  cache.saveDf(df, dfName)
  return df
  
def reportRoute(cache):
  df = analyzeRoute(cache)
  log(df[['src', 'country', 'rtt', 'drtt', 'naive_pred', 'cimbala_pred', 'cimbalaAlt_pred']], level = 'deepUser')
  return df

############################################################
# S: Analyze aggregate of all routes #######################

Nodes = {}
Edges = {}

def addRouteToGraph(df):
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
  df['distance'] = np.sqrt(df['lat'].diff() ** 2 + df['long'].diff() ** 2)

  df.apply(row2Edge, axis = 'columns')
  df.drop(['prev', 'distance'], axis = 'columns', inplace = True)

def reportGraph(dfNodes, dfEdges, cache):
  # TODO: Cache

  G = nx.Graph()
  for v, row in dfNodes.iterrows():
    G.add_node(v, **row.to_dict())

  for (v, u), row in dfEdges.iterrows():
    G.add_edge(v, u, **row.to_dict())
  
  log(G, level = 'user')
  graphPlot(G, dfNodes, dfEdges)

def reportAggregate(cache):
  # TODO: Cache

  # Calculate aggregate
  dfNodes = pd.DataFrame([
    {'count': len(data), **data[0]} # TODO: data[0] check it was labeled the same every time
    for data in Nodes.values()
  ], index = Nodes.keys())
  dfEdges = pd.DataFrame([
    {
      'count': len(data),
      'rtt': np.mean([dataPoint['rtt'] for dataPoint in data]),
      'length': data[0]['length'], # TODO: Check no differences in location labeling
      'naive_pred_mean': np.mean([int(dataPoint['naive_pred']) for dataPoint in data]),
      'cimbala_pred_mean': np.mean([int(dataPoint['cimbala_pred']) for dataPoint in data]),
      'cimbalaAlt_pred_mean': np.mean([int(dataPoint['cimbalaAlt_pred']) for dataPoint in data]),

      'lat': (dfNodes.at[v, 'lat'], dfNodes.at[u, 'lat']),
      'long': (dfNodes.at[v, 'long'], dfNodes.at[u, 'long']),
    }
    for (v, u), data in Edges.items()
  ], index = Edges.keys())

  naiveMethod(dfEdges, 'rtt')
  cimbalaMethod(dfEdges, 'rtt')
  cimbalaMethod(dfEdges, 'rtt', altCutoff = 0.02) # TODO: altCutoff

  log(dfEdges[['count', 'rtt', 'naive_pred', 'naive_pred_mean', 'cimbala_pred', 'cimbala_pred_mean', 'cimbalaAlt_pred', 'cimbalaAlt_pred_mean']], level = 'deepUser')
  worldPlot(dfNodes, dfEdges)
  reportGraph(dfNodes, dfEdges, cache)
  droppedPlot(dropNa, dropDrtt)

############################################################

if __name__ == '__main__':
  # pd.set_option('display.max_columns', None)
  # pd.set_option('display.max_rows', None)

  files = sys.argv[1:] if len(sys.argv) >= 2 else utils.getAllDataFiles()
  save = True
  load = True

  for fpath in files:
    fbase = fpath[:-4] # Remove .pkl
    cache = Cache(fbase, save, load)
    if cache.loadPickle() is None:
      log('[analyzeCase] No pickle for {fbase}', level = 'error')
    else:
      try:
        reportRoute(cache)
      except:
        pass
  reportAggregate(cache)
