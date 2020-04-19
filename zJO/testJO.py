# -*- coding: utf-8 -*-


from multiprocessing import Pool
import time

def f(x):
    init = time.time()
    for i in range(1,10):
        time.sleep(1)
    fin = time.time()
    return fin-init



if __name__ == '__main__':
    with Pool(16) as p:
        print(p.map(f, [1, 2, 3]))
        
        
f([1, 2, 3])
