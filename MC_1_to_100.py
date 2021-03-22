# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 21:10:59 2016

@author: mjigmond
"""

from pandas import read_excel
from itertools import islice
import numpy as np
import os
from subprocess import Popen, PIPE
from time import sleep
from shutil import copy2


outpath = 'MC_1_to_100'
if not os.path.exists(outpath): os.makedirs(outpath)

xlsxFile = 'Input_MC_HAA_morris4b_random_1_to_100.xlsx'
frozen_sheet = 'Frozen'
heat_sheet = 'heat_rates'

dfData = read_excel(xlsxFile, sheetname=frozen_sheet, header=None).fillna(method='ffill', axis=1)
heatData = read_excel(xlsxFile, sheetname=heat_sheet, header=None, skiprows=3, parse_cols='I:V').values

baseFile = 'TH4_2Dgh16_bc2'
nsim = 100
cpumax = 4

ELRN = {}
with open(baseFile, 'r') as f:
    elem = 0
    for line in f:
        if line.startswith('ELEME'):
            elem = 1
        elif line.startswith('CONNE-'):
            break
        elif elem:
            try:
                el = line[:10].strip()
                rn = line[10:20].strip()
                ELRN[el] = rn
            except:
                break

rockList = []
with open(baseFile, 'r') as f:
    hdr = list(islice(f, 10))
    while 1:
        rock = list(islice(f, 4))
        if rock[1].startswith('START'):
            break
        rn = rock[0][:9].strip()
        rockList.append(rn)

SEN = {}
rocks = []
for rn in dfData.values[0][4:]:
    if rn.startswith('ALL EDZ'):
        edz = [x for x in rockList if x.startswith('EDZ')]
        for n in edz:
            SEN.setdefault(n, {
                'Kx':np.zeros(nsim)
                ,'Ky':np.zeros(nsim)
                ,'Kz':np.zeros(nsim)
                ,'TC':np.zeros(nsim)
                ,'HC':np.zeros(nsim)
                ,'Cp':np.zeros(nsim)
                ,'Ct':np.zeros(nsim)
                ,'phi':np.zeros(nsim)
            })
        rocks.append(edz)
    elif ',' in rn:
        rnlist = [x.strip() for x in rn.split(',')]
        for n in rnlist:
            if n in rockList:
                SEN.setdefault(n, {
                    'Kx':np.zeros(nsim)
                    ,'Ky':np.zeros(nsim)
                    ,'Kz':np.zeros(nsim)
                    ,'TC':np.zeros(nsim)
                    ,'HC':np.zeros(nsim)
                    ,'Cp':np.zeros(nsim)
                    ,'Ct':np.zeros(nsim)
                    ,'phi':np.zeros(nsim)
                })
        rocks.append(rnlist)
    elif rn in rockList:
        SEN.setdefault(rn, {
            'Kx':np.zeros(nsim)
            ,'Ky':np.zeros(nsim)
            ,'Kz':np.zeros(nsim)
            ,'TC':np.zeros(nsim)
            ,'HC':np.zeros(nsim)
            ,'Cp':np.zeros(nsim)
            ,'Ct':np.zeros(nsim)
            ,'phi':np.zeros(nsim)
        })
        rocks.append([rn])
    else:
        pass

keys = dfData.values[1]
par = {}
for v in dfData.values[5:]:
    sim = v[2]
    par[sim] = v[3]
    if sim == 1:
        par[sim] = 0
    for i, vv in enumerate(v[4:]):
        k = keys[i+4].strip()
        rk = rocks[i]
        if k.startswith('abs'):
            continue
        elif k == 'Kxyz':
            for r in rk:
                SEN[r]['Kx'][sim-1] = vv
                SEN[r]['Ky'][sim-1] = vv
                SEN[r]['Kz'][sim-1] = vv
        elif k == 'Kxy':
            for r in rk:
                SEN[r]['Kx'][sim-1] = vv
                SEN[r]['Ky'][sim-1] = vv
        elif k == 'Kx':
            for r in rk:
                SEN[r]['Kx'][sim-1] = vv
        elif k == 'Ky':
            for r in rk:
                SEN[r]['Ky'][sim-1] = vv
        elif k == 'Kz':
            for r in rk:
                SEN[r]['Kz'][sim-1] = vv
        elif k == 'TC':
            for r in rk:
                SEN[r]['TC'][sim-1] = vv
        elif k == 'HC':
            for r in rk:
                SEN[r]['HC'][sim-1] = vv
        elif k == 'Cp':
            for r in rk:
                if r != 'CANIS':
                    SEN[r]['Cp'][sim-1] = vv
        elif k == 'Ct':
            for r in rk:
                SEN[r]['Ct'][sim-1] = vv
        elif k == 'phi':
            for r in rk:
                SEN[r]['phi'][sim-1] = vv
        elif k.startswith('phi '):
            r = k.split()[1]
            SEN[r]['phi'][sim-1] = vv

with open(baseFile, 'r') as f:
    blines = f.readlines()

for k, v in sorted(par.items()):
    if k in range(1,11): continue
    npth = '{}/run{:03d}'.format(outpath, k)
    if not os.path.exists(npth):
        os.makedirs(npth)
    fn = '{}/{}_run{:03d}_param{}'.format(npth, baseFile, k, v)
    with open(fn, 'w') as f:
        f.writelines(blines[:10])
        i = 10
        while 1:
            lines = blines[i:i+4]
            if lines[1].startswith('START'):
                f.writelines(lines)
                break
            rn = lines[0][:9].strip()
            if rn in SEN:
                ln = lines[0][:30]
                ln += '{:10.4e}'.format(SEN[rn]['Kx'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['Ky'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['Kz'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['TC'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['HC'][k-1])
                lines[0] = ln + lines[0][80:]
                if rn != 'CANIS':
                    ln = '{:10.4e}'.format(SEN[rn]['Cp'][k-1])
                else:
                    ln = lines[1][:10]
                ln += '{:10.4e}'.format(SEN[rn]['Ct'][k-1])
                lines[1] = ln + lines[1][20:]
                f.writelines(lines)
            else:
                f.writelines(lines)
            i += 4
        f.writelines(blines[i+4:7147])
        i = 7147
        while i < 12455:
            lines = blines[i:i+2]
            el = lines[0][:16].strip()
            if el in ELRN:
                rn = ELRN[el]
                if rn in SEN and rn == 'OPAM1':
                    lines[0] = lines[0][:16] + '{:14.8e}\n'.format(SEN[rn]['phi'][k-1])
            f.writelines(lines)
            i += 2
        f.writelines(blines[12455:12649])
        hlines = []
        for j in range(0, 12, 4):
            hlines.append('{:14.4E}{:14.4E}{:14.4E}{:14.4E}\n'.format(*heatData[k-1,j:j+4]))
        hlines.append('{:14.4E}{:14.4E}\n'.format(*heatData[k-1,12:14]))
        for j in range(12649, 12649+9*18, 9):
            lines = blines[j:j+9]
            f.writelines(lines[:5])
            f.writelines(hlines)
        f.writelines(blines[12811:])
    with open('{}/tough2.in'.format(npth), 'w') as f:
        f.write('invdir\n{}\n'.format(os.path.basename(fn)))
    copy2('invdir', npth)
    while 1:
        cpus = Popen(['tasklist', '/fi', "Imagename eq it2_5xl.exe"], stdout=PIPE).communicate()[0].split('\r\n')
        if len(cpus) < cpumax+4:
            os.chdir(npth)
            with open('tough2.in'.format(k, v), 'r') as f, open(os.devnull, 'w') as dnull:
                Popen(['../../it2_5xl.exe'], stdin=f, stdout=dnull) # using stdout=PIPE causes some process lockup
            os.chdir('../..')
            break
        sleep(10)
