#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE


text = '''
    set title "%(title)s" font "Times-New-Roman,24"
    set terminal pngcairo size 900,900 font "Helvetica,14" 
    set output "%(output)s"
    set xrange [%(xrange)s]
    set yrange [%(yrange)s]
    plot "%(file)s" using 1:2 pt 7 ps 0.8
'''

params = {
    'xrange': '0:1',
    'yrange': '0:1',
}


for name in sys.argv[1:]:
    #name = sys.argv[1]
    #out = sys.argv[2]
    out = name.replace('.dat', '.png')
    title = 'Step'

    conf = {
        'file': name,
        'output': out,
        'title': title,
    }

    cmd = text % dict(params, **conf)

    print name, '>', out
    p = Popen(['gnuplot'], shell=True, stdin=PIPE)
    p.communicate(cmd)

