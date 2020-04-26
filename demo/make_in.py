import random
import time
import math


def work():
    n = int(input())
    # n,m,p,q = map(int, input().split())
    print(random.randint(1, n), random.randint(1, n))


try:
    work()
except KeyboardInterrupt:
    pass