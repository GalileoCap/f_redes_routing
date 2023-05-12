import os
import pickle

OUTDIR = 'out'
DATADIR = 'data'

def mkDirs():
  os.makedirs(OUTDIR, exist_ok = True)
  os.makedirs(DATADIR, exist_ok = True)

def genPath(_dir, fname, extension):
  return os.path.join(_dir, fname + extension)
def pklPath(fname):
  return genPath(DATADIR, fname, '.pkl')

def getAllDataFiles():
  return [
    os.path.join(DATADIR, fname)
    for fname in os.listdir(DATADIR)
    if os.path.isfile(os.path.join(DATADIR, fname))
  ]

def savePicklePath(data, fpath):
  log(f'[savePicklePath] {fpath=}', level = 'debug')
  mkDirs()
  with open(fpath, 'wb') as fout:
    pickle.dump(data, fout)
def loadPicklePath(fpath):
  log(f'[loadPicklePath] {fpath=}', level = 'debug')
  if os.path.isfile(fpath):
    with open(fpath, 'rb') as fout:
      return pickle.load(fout)
  return None

def savePickle(data, fname):
  return savePicklePath(data, pklPath(fname))
def loadPickle(fname):
  return loadPicklePath(pklPath(fname))

def log(*args, level):
  # TODO: Filter
  print(*args)

