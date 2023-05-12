#!/usr/bin/env python3
import scapy.all as scapy

import sys
from time import *
from datetime import datetime

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
    else:
      log(f'[pingTtl] No answer {ttl=} {i=}', level = 'deepDebug')

  return res, success

def traceroute(dst, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  log(f'[traceroute] {dst=} {maxTtl=}, {n=}, {timeout=}, {maxRetries=}', level = 'user')

  data, success = [], False
  for ttl in range(1, maxTtl):
    ttlData, _success = pingTtl(dst, ttl, n, timeout, maxRetries)
    data.append(ttlData)
    if _success:
      success = True
      break

  log(f'[traceroute] {success=}', level = 'user')
  return data, success

def tracerouteHosts(hosts, fbase, save = True, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  data = {
    host: traceroute(host, maxTtl, n, timeout, maxRetries)
    for host in hosts
  }

  if save:
    utils.savePickle(((maxTtl, n, timeout, maxRetries), data), fbase)
  return data

if __name__ == '__main__':
  user = sys.argv[1]
  date = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
  fbase = f'{user}_{date}'

  hosts = [
    'galileocap.me', 'youtube.com',
    'argentina.gob.ar',
    # 'dc.uba.ar',
  ]
  tracerouteHosts(hosts, fbase, n = 5)
