# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 21:10:59 2016

@author: mjigmond
"""

from pandas import read_excel
from itertools import islice
import numpy as np
import os


out_path = 'Morris.Set1/input'
if not os.path.exists(out_path): os.makedirs(out_path)

xlsxFile = 'Input_Morris_Screening_v2.xlsx'
sheet_name = 'input_parameters (2)'

baseFile = 'tough2_input/SMA3Dn_R09_1_gas'
incFile = 'tough2_input/SMA3Dn_R09_1_gas.incon'
elemFile = 'modify_incon_eos5/SMA3Dn_R09_1_gas.eleme'

ELRN = {}
with open(elemFile, 'r') as f:
    f.readline()
    for line in f:
        el = line[:10].strip()
        rn = line[10:20].strip()
        ELRN[el] = rn

rockList = []
with open(baseFile, 'r') as f:
    hdr = list(islice(f, 10))
    while 1:
        rock = list(islice(f, 4))
        if rock[0].startswith('TOP '):
            break
        rn = rock[0][:9].strip()
        rockList.append(rn)

dfData = read_excel(xlsxFile, sheetname=sheet_name, header=None).fillna(method='ffill', axis=1)

SEN = {}
rocks = []
for rn in dfData.values[0]:
    if rn.startswith('ALL EDZ'):
        edz = [x for x in rockList if x.startswith('EDZ')]
        for n in edz:
            SEN.setdefault(n, {
                'Kx':np.zeros(25)
                ,'Ky':np.zeros(25)
                ,'Kz':np.zeros(25)
                ,'P0':np.zeros(25)
                ,'n':np.zeros(25)
                ,'Slr':np.zeros(25)
                ,'phi':np.zeros(25)
            })
        rocks.append(edz)
    elif ',' in rn:
        rnlist = [x.strip() for x in rn.split(',')]
        for n in rnlist:
            if n in rockList:
                SEN.setdefault(n, {
                    'Kx':np.zeros(25)
                    ,'Ky':np.zeros(25)
                    ,'Kz':np.zeros(25)
                    ,'P0':np.zeros(25)
                    ,'n':np.zeros(25)
                    ,'Slr':np.zeros(25)
                    ,'phi':np.zeros(25)
                })
        rocks.append(rnlist)
    elif rn in rockList:
        SEN.setdefault(rn, {
            'Kx':np.zeros(25)
            ,'Ky':np.zeros(25)
            ,'Kz':np.zeros(25)
            ,'P0':np.zeros(25)
            ,'n':np.zeros(25)
            ,'Slr':np.zeros(25)
            ,'phi':np.zeros(25)
        })
        rocks.append([rn])
    else:
        pass

keys = dfData.values[1]
par = {}
for v in dfData.values[5:]:
    sim = v[2]
    run = v[3].split()
    par[sim] = run[-1]
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
        elif k == 'P0':
            for r in rk:
                SEN[r]['P0'][sim-1] = vv
        elif k == 'n':
            for r in rk:
                SEN[r]['n'][sim-1] = vv
        elif k == 'Slr':
            for r in rk:
                SEN[r]['Slr'][sim-1] = vv
        elif k == 'phi':
            for r in rk:
                SEN[r]['phi'][sim-1] = vv
        elif k.startswith('phi '):
            r = k.split()[1]
            SEN[r]['phi'][sim-1] = vv

with open(baseFile, 'r') as f:
    blines = f.readlines()

with open(incFile, 'r') as f:
    ilines = f.readlines()

for k, v in sorted(par.items()):
    fn = '{}/SMA3Dn_R09_1_gas_run{}_param{}'.format(out_path, k, v)
    with open(fn, 'w') as f:
        f.writelines(blines[:10])
        i = 10
        while 1:
            lines = blines[i:i+4]
            if lines[0].startswith('TOP '):
                f.writelines(lines)
                break
            rn = lines[0][:9].strip()
            if rn in SEN:
                ln = lines[0][:30]
                ln += '{:10.4e}'.format(SEN[rn]['Kx'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['Ky'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['Kz'][k-1])
                lines[0] = ln + lines[0][60:]
                ln = lines[2][:10]
                ln += '{:10.4e}'.format(SEN[rn]['Slr'][k-1])
                lines[2] = ln + lines[2][20:]
                ln = lines[3][:10]
                ln += '{:10.4e}'.format(SEN[rn]['n'][k-1])
                ln += '{:10.4e}'.format(SEN[rn]['P0'][k-1])
                lines[3] = ln + lines[3][30:]
                f.writelines(lines)
            else:
                f.writelines(lines)
            i += 4
        f.writelines(blines[i+4:])
    fn = '{}/SMA3Dn_R09_1_gas_run{}_param{}.incon'.format(out_path, k, v)
    with open(fn, 'w') as f:
        f.write(ilines[0])
        i = 1
        while 1:
            lines = ilines[i:i+2]
            if lines[0].startswith('+++'):
                f.writelines(ilines[i:])
                break
            el = lines[0][:16].strip()
            rn = ELRN[el]
            if rn in SEN:
                lines[0] = lines[0][:16] + '{:14.8e}\n'.format(SEN[rn]['phi'][k-1])
                f.writelines(lines)
            else:
                f.writelines(lines)
            i += 2
