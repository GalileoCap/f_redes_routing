# https://dev.galileocap.me/udo

UDOConfig = {
  'version': (1, 3, 0)
}

def TaskEntrega():
  infiles = ['./Pipfile', './Pipfile.lock', './README.md', './src']
  ofile = 'entrega.zip'

  return {
    'name': 'entrega',
    'outs': [ofile],
    'skipRun': True,

    'actions': [
      f'zip {ofile} {" ".join(infiles)} -r9' # TODO: Put inside a subdir
    ],
  }

def TaskTraceroute():
  return {
    'name': 'traceroute',
    'outs': ['data'],
    'skipRun': True,

    'capture': 1,
    'actions': [
      'pipenv run sudo python src/traceroute.py $USER'
    ],
  }

def TaskAnalyze():
  return {
    'name': 'analyze',
    'outs': ['out'],
    'skipRun': True,

    'capture': 1,
    'actions': [
      'pipenv run sudo python src/analyze.py'
    ],
  }
