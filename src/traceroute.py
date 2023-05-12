#!/usr/bin/env python3
import scapy.all as scapy
import numpy as np
import threading

import sys
from time import *
from datetime import datetime

from analyze import process
from cache import Cache
import utils
from utils import log

def pingTtl(dst, ttl, n = 30, timeout = 0.8, maxRetries = 5):
  res, success = [], False
  
  for i in range(n):
    for j in range(maxRetries): # To handle ans = None
      probe = scapy.IP(dst = dst, ttl = ttl) / scapy.ICMP()
      t_i = time()
      ans = scapy.sr1(probe, verbose = False, timeout = timeout)
      t_f = time()
      rtt = t_f - t_i

      if ans is not None:
        res.append({'src': ans.src, 'rtt': rtt})
        success |= ans[scapy.ICMP].type == 0 # TODO: Check this is correct
        break

  if len(res) == 0:
    log(f'[pingTtl] No answers {dst=} {ttl=}', level = 'warning')
  return res, success

def traceroute(dst, cache, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  log(f'[traceroute] START {dst=} {maxTtl=}, {n=}, {timeout=}, {maxRetries=}', level = 'user')

  pingTtl(dst, maxTtl + 1, n = 1)

  data, success = [], False
  for ttl in range(1, maxTtl):
    ttlData, _success = pingTtl(dst, ttl, n, timeout, maxRetries)
    data.append(ttlData)
    if _success:
      success = True
      break

  res = ((maxTtl, n, timeout, maxRetries, success), data)
  cache.savePickle(res)
  log(f'[traceroute] END {success=}', level = 'user')
  return res

def tracerouteHosts(hosts, fbase, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  for dst in hosts:
    try:
      cache = Cache(f'{fbase}_{dst}', load = False)
      traceroute(dst, cache, maxTtl, n, timeout, maxRetries)
      process(cache)
    except Exception as e:
      log(f'[tracerouteHosts] ERROR {dst=}: {e}', level = 'error')

if __name__ == '__main__':
  user = sys.argv[1]
  hostsPath = sys.argv[2]
  date = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
  fbase = f'{user}_{date}'

  hosts = []
  with open(hostsPath, 'r') as fin:
    hosts = fin.read().splitlines()

  threads = []
  for idx, tHosts in enumerate(np.array_split(hosts, 10)):
    # t = threading.Thread(target = tracerouteHosts, args = (tHosts, fbase), kwargs = {'maxTtl': 5, 'n': 1}) # TODO: Remove kwargs to use default
    t = threading.Thread(target = tracerouteHosts, args = (tHosts, fbase))
    threads.append(t)
    t.start()

  for t in threads:
    t.join()
  log('ALL DONE', level = 'user')
