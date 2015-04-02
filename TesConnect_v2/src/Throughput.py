#!/usr/bin/env python
#
#  pinger.py
#  Host/Device Ping Utility for Windows
#  Corey Goldberg (www.goldb.org), 2008
#
#
#  Pinger uses your system's ping utility to send an ICMP ECHO_REQUEST 
#  to a list of hosts or devices.  This is useful for measuring network
#  latency and verifying hosts are alive.
from __future__ import division


import re
from subprocess import Popen, PIPE
from threading import Thread

def getThroughput(host):
	p = Popen('ping -n 1 ' + host, stdout=PIPE)
	m = re.search('Average = (.*)ms', p.stdout.read())
	if m: print 'Round Trip Time: %s ms -' % m.group(1), host
	else: print 'Error: Invalid Response -', host
	if float(m.group(1))==0:
		return 0
	latency=float(m.group(1))/1000
	th=524288/latency
	return "{0:.2f}".format(round(th/1000000,2))
