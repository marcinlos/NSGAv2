#!/usr/bin/env python

import sys
import re
from subprocess import Popen, PIPE


text = '''
    set title "%(title)s" font "Times-New-Roman,24"
    set terminal pngcairo size 900,900 font "Helvetica,14"
    set output "%(output)s"
    set xrange [%(xrange)s]
    set yrange [%(yrange)s]
    plot "%(file)s" using 1:2 pt 7 ps 0.8 notitle,\
         "%(exact)s" using 1:2 with lines title "Exact front"
    print("%(file)s > %(output)s")
'''

params = {
    'xrange': '0:1',
    'yrange': '0:1',
}

def get_step(name):
    nums = re.findall(r'\d+', name)
    return nums[0] if nums else '(?)'

p = Popen(['gnuplot'], shell=True, stdin=PIPE)
exact = sys.argv[1]

for name in sys.argv[2:]:
    out = name.replace('.dat', '.png')
    step = get_step(name)
    title = 'Step %s' % step

    conf = {
        'file': name,
        'output': out,
        'title': title,
        'exact': exact,
    }

    cmd = text % dict(params, **conf)
    p.stdin.write(cmd)

p.communicate()

