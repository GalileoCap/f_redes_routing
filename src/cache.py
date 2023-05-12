import os
import pickle

import utils

class Cache:
  def __init__(self, fbase, save = True, load = True):
    self.fbase = fbase
    self.save = save
    self.load = load

    self.dfs = {}

  def saveDf(self, df, name):
    self.dfs[name] = df
    if self.save:
      utils.saveDf(df, self.fbase, name)
  def loadDf(self, name):
    if not self.load:
      return None

    if name not in self.dfs.keys():
      df = utils.loadDf(self.fbase, name)
      if df is None:
        return None
      self.dfs[name] = df
    return self.dfs[name]

  # TODO: loadAll
  def flush(self):
    for name, df in self.dfs.items():
      self.saveDf(df, name)
