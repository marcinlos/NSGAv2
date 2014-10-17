
import IntOb.NSGAv2 as nsga

f = lambda (x, y): x
g = lambda (x, y): 1 - x * y

bounds = [(0,1),(0,1)] 
ranges = [(0,1),(0,1)] 

def onStep(step, P):

    if step % 1 == 0:
        print 'step', step
        with open('step_{:04}.dat'.format(step), 'w') as out:
            for p in P:
                x = f(p)
                y = g(p)
                line = '{:20} {:20}\n'.format(x, y)
                out.write(line)


alg = nsga.NSGA((f, g), bounds, ranges) 
solution = alg.optimize(20, onStep)

