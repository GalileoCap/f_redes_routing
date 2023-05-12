import os
import pickle

import utils

class Cache:
  def __init__(self, fbase, save = True, load = True):
    self.fbase = fbase
    self.save = save
    self.load = load

    self.dfs = {}
    self.data = None

  def savePickle(self, data):
    self.data = data
    if self.save:
      utils.savePickle(data, self.fbase)
  def loadPickle(self):
    if not self.load:
      return self.data

    if self.data is None:
      self.data = utils.loadPickle(self.fbase)
    return self.data

  def saveDf(self, df, name):
    self.dfs[name] = df
    if self.save:
      utils.saveDf(df, self.fbase, name)
  def loadDf(self, name):
    if not self.load:
      return self.dfs.get(name, None)

    if name not in self.dfs.keys():
      self.dfs[name] = utils.loadDf(self.fbase, name)
    return self.dfs[name]

  # TODO: loadAll
  def flush(self):
    for name, df in self.dfs.items():
      self.saveDf(df, name)
    self.savePickle(self.data)
