# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 21:10:59 2016

Cheap parallelization of a serial process

@author: mjigmond
"""

from subprocess import Popen, PIPE
from time import sleep

baseFile = 'TH4_2Dgh16_bc2'
node = 'node01'

cpumax = 16
for i in range(32):
    npth = '/workspace/hlw.2d/set1/run{}'.format(i+1)
    while 1:
        cpus = Popen(['ssh', node, 'ps', '-C', 'it2_5xl.exe'], stdout=PIPE).communicate()[0].split('\n')
        cpus = len(cpus) - 1
        if cpus < cpumax:
            Popen(
                ['ssh', node, 'cd {};../../it2_5xl.exe < tough2.in > /dev/null &'.format(npth)],
                stdout=PIPE
            ).communicate()
            break
        sleep(10)
