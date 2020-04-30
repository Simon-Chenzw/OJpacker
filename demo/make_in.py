import random


def work():
    n = int(input())
    print(random.randint(1, n), random.randint(1, n))


try:
    work()
except KeyboardInterrupt:
    pass