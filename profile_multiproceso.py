import cProfile

from multiprocesos import *

n = 10000000
arry = array(n)

print('*'*80)
print('Lineal')
print('*'*80)
with cProfile.Profile() as pr:
    _ = lineal(arry)
pr.print_stats()

print('*'*80)
print('Parallel')
print('*'*80)
with cProfile.Profile() as pr:
    _ = parallel(arry)
pr.print_stats()
print('*'*80)
