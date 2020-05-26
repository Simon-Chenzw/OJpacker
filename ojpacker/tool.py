try:
    import colorful
except ImportError:
    pass

import time
import threading


def yesorno(output_str):
    while True:
        s = input(color("purple", output_str + " [Y/n] "))
        if s in "Yy":
            return True
        elif s in "Nn":
            return False


def color(color, string):
    """
    color: yellow, orange, red, magenta, violet, blue, cyan, green
    """
    if "colorful" in globals():
        return ("{cf.%s}%s{cf.reset}" % (color, string)).format(cf=colorful)
    else:
        return string


def readable_byte(value):
    unit = ["B", "KB", "MB", "GB"]
    level = 0
    while (value >= 1024):
        value /= 1024
        level += 1
    return "%.2f %s" % (value, unit[level])


def exec_thread_pool(thread_pool, multi_thread=False):
    def thread_pool_watcher():
        cnt = 0
        while cnt != len(thread_pool):
            time.sleep(0.1)
            cnt = 0
            for i in range(len(thread_pool)):
                if thread_pool_started[i] and not thread_pool[i].is_alive():
                    print("✓", end="")
                    cnt += 1
                else:
                    print("✗", end="")
            print(" %2d/%2d\r" % (cnt, len(thread_pool)), end="")
        print()

    thread_pool_started = [False] * len(thread_pool)
    watcher = threading.Thread(target=thread_pool_watcher)
    watcher.start()
    for i in range(len(thread_pool)):
        thread_pool[i].start()
        thread_pool_started[i] = True
        if not multi_thread:
            thread_pool[i].join()
    watcher.join()
