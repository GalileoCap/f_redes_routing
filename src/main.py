#!/usr/bin/env python3
import scapy.all as scapy

import pandas as pd
import sys
from time import *

def log(*args, level):
  # TODO: Filter
  print(*args)

def pingTtl(dst, ttl, n = 30, timeout = 0.8, maxRetries = 5):
  res = []
  
  for i in range(n):
    for j in range(maxRetries): # To handle ans = None
      probe = scapy.IP(dst = dst, ttl = ttl) / scapy.ICMP()
      t_i = time()
      ans = scapy.sr1(probe, verbose = False, timeout = timeout)
      t_f = time()
      rtt = t_f - t_i

      if ans is not None:
        res.append((ans.src, rtt))
        break
    else:
      log(f'[pingTtl] No answer {ttl=} {i=}', level = 'deepDebug')

  return res

def traceroute(dst, maxTtl = 64, n = 30, timeout = 0.8, maxRetries = 5):
  log(f'[traceroute] {dst=} {maxTtl=}, {n=}, {timeout=}, {maxRetries=}', level = 'user')

  data = []
  for ttl in range(1, maxTtl):
    pingData = pingTtl(sys.argv[1], ttl, n, timeout, maxRetries)
    data += [
      {
        'src': src,
        'rtt': rtt,
        'ttl': ttl,
      }
      for src, rtt in pingData
    ]
  return pd.DataFrame(data)

if __name__ == '__main__':
  df = traceroute(sys.argv[1], 5, 2, maxRetries = 1)
  print(df.head())
