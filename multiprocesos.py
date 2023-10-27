from multiprocessing import Pool, cpu_count

def array(n):
    return list(range(n))

def f(x):
    return x*x

def lineal(arry):
    return [ f(x) for x in arry ]

def parallel(arry):
    n = cpu_count()
    p = Pool(n)
    return p.map(f, arry)

def run(n):
    arry = array(n)
    print(lineal(arry))
    print(parallel(arry))

if __name__ == '__main__':
    run(1000000)
