#!/usr/bin/env python3
import scapy.all as scapy

import sys
from time import *
from datetime import datetime

import analyze
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
    else:
      log(f'[pingTtl] No answer {ttl=} {i=}', level = 'deepDebug')

  return res, success

def traceroute(dst, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  log(f'[traceroute] {dst=} {maxTtl=}, {n=}, {timeout=}, {maxRetries=}', level = 'user')

  pingTtl(dst, maxTtl + 1, n = 1)

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

  res = ((maxTtl, n, timeout, maxRetries), data)
  if save:
    utils.savePickle(res, fbase)
  return res

if __name__ == '__main__':
  user = sys.argv[1]
  hostsPath = sys.argv[2]
  date = datetime.now().strftime("%y-%m-%d_%H-%M-%S")
  fbase = f'{user}_{date}' #TODO: user_host_date

  hosts = []
  with open(hostsPath, 'r') as fin:
    hosts = fin.read().splitlines()

  info, data = tracerouteHosts(hosts, fbase, maxTtl= 5, n = 1)
  analyze.analyze(info, data, Cache(fbase, load = False))
