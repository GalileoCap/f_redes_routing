import os
import pickle

import pandas as pd

OUTDIR = 'out'
DATADIR = 'data'

logMask = [
  'user',
  # 'deepUser',
  # 'debug',
  'error',
  # 'deepDebug',
]

def mkDirs(fpath):
  os.makedirs(fpath, exist_ok = True)
def joinPath(*args):
  return os.path.join(*args)

def pklPath(fbase):
  return joinPath(DATADIR, fbase + '.pkl')
def dfPath(fbase, name):
  return joinPath(OUTDIR, fbase, name + '.csv.tar.gz')
def htmlPath(name):
  return joinPath(OUTDIR, name + '.html')
def imgPath(name):
  return joinPath(OUTDIR, name + '.pdf')

def getAllDataFiles():
  return [
    fname
    for fname in os.listdir(DATADIR)
    if os.path.isfile(os.path.join(DATADIR, fname))
  ]

def savePicklePath(data, fpath):
  log(f'[savePicklePath] {fpath=}', level = 'deepDebug')
  with open(fpath, 'wb') as fout:
    pickle.dump(data, fout)
def loadPicklePath(fpath):
  if os.path.isfile(fpath):
    log(f'[loadPicklePath] {fpath=}', level = 'deepDebug')
    with open(fpath, 'rb') as fout:
      return pickle.load(fout)
  return None

def saveDfPath(df, fpath):
  log(f'[saveDfPath] {fpath=}', level = 'deepDebug')
  df.to_csv(fpath)
def loadDfPath(fpath):
  if os.path.isfile(fpath):
    log(f'[loadDfPath] {fpath=}', level = 'deepDebug')
    return pd.read_csv(fpath, index_col = 0)
  return None

def savePickle(data, fbase):
  mkDirs(DATADIR)
  return savePicklePath(data, pklPath(fbase))
def loadPickle(fbase):
  return loadPicklePath(pklPath(fbase))
def saveDf(df, fbase, name):
  mkDirs(joinPath(OUTDIR, fbase)) # TODO: Clean
  return saveDfPath(df, dfPath(fbase, name))
def loadDf(fbase, name):
  return loadDfPath(dfPath(fbase, name))

def saveFig(fig, name):
  mkDirs(OUTDIR)
  fpath = htmlPath(name)
  fig.write_html(fpath)

  fpath = imgPath(name)
  fig.write_image(fpath)

def log(*args, level):
  if level in logMask:
    print(*args)

