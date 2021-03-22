# -*- coding: utf-8 -*-
"""
Created on Thu Sep 01 08:34:35 2016

@author: mjigmond
"""

from pandas import read_excel
from subprocess import Popen, PIPE
from shutil import copy2

notes_file = 'Andra_THM_2D_1_w_notes'
thermal_file = 'Andra Thermal Loading plot_v2.xlsx'

df = read_excel(thermal_file, sheetname='Sheet1', skiprows=4, parse_cols=range(7), header=None)

ix = {}
with open(notes_file, 'r') as f:
    blines = f.readlines()
    f.seek(0)
    for i, line in enumerate(f):
        if 'INITIAL_TIME' in line:
            ix['IT'] = (i, len('INITIAL_TIME'))
        elif 'ETIME_HERE' in line:
            ix['ET'] = (i, len('ETIME_HERE'))
        elif 'TEMPERATURE_IS_HERE' in line:
            ix.setdefault('T', [])
            ix['T'].append((i, len('TEMPERATURE_IS_HERE')))
        elif 'INCON' in line:
            ix['INCON'] = i

times = []
for i, d in enumerate(df.values):
    print(i, d)
    nlines = blines[:]
    fn = 'Andra_THM_2D_{:02d}'.format(i+1)
    if i == 0:
        for k, v in ix.items():
            if k == 'T':
                for j, l in v:
                    nlines[j] = blines[j].replace('TEMPERATURE_IS_HERE', '%.13E' % d[6])
            elif k == 'ET':
                nlines[v[0]] = blines[v[0]].replace('ETIME_HERE', '{:.5E}'.format(d[4]).replace('+', ''))
            elif k == 'IT':
                nlines[v[0]] = blines[v[0]].replace('INITIAL_TIME', '{:.5E}'.format(d[2]))
        with open(fn, 'w') as f:
            f.writelines(nlines)
        with open('tough2.in', 'w') as f:
            f.write('invdir\n{}\n'.format(fn))
        with open('tough2.in', 'r') as f:
            p = Popen(['it2_5xl.exe'], stdin=f, stdout=PIPE).communicate()
        copy2('SAVE', 'SAVE.{}'.format(fn))
        copy2('FOFT', 'FOFT.{}'.format(fn))
        with open('SAVE.{}'.format(fn), 'r') as f:
            efft = float(f.readlines()[-1].split()[-1])
            times.append((d[4], efft, d[4]-efft))
    else:
        j = ix['INCON']
        with open('SAVE.Andra_THM_2D_{:02d}'.format(i), 'r') as f:
            lines = f.readlines()[1:]
        nlines[j+1:len(lines)+j+1] = lines[:]
        for k, v in ix.items():
            if k == 'T':
                for j, l in v:
                    nlines[j] = blines[j].replace('TEMPERATURE_IS_HERE', '%.13E' % d[6])
            elif k == 'ET':
                nlines[v[0]] = blines[v[0]].replace('ETIME_HERE', '{:.5E}'.format(d[4]).replace('+', ''))
        with open(fn, 'w') as f:
            f.writelines(nlines)
        with open('tough2.in', 'w') as f:
            f.write('invdir\n{}\n'.format(fn))
        with open('tough2.in', 'r') as f:
            p = Popen(['it2_5xl.exe'], stdin=f, stdout=PIPE).communicate()
        copy2('SAVE', 'SAVE.{}'.format(fn))
        copy2('FOFT', 'FOFT.{}'.format(fn))
        with open('SAVE.{}'.format(fn), 'r') as f:
            efft = float(f.readlines()[-1].split()[-1])
            times.append((d[4], efft, d[4]-efft))

with open('end_time_deltas.csv', 'w') as f:
    f.write('simulation,prescribed,effective,delta\n')
    for i, t in enumerate(times):
        f.write('{},{},{},{}\n'.format(i+1, *t))
