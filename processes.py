import os
import random
from multiprocessing import Process
from time import sleep


def random_time():
    for _ in range(10):
        print(f"From process: {os.getpid()}")
        sleep(random.randint(1, 3))


if __name__ == "__main__":
    process_1 = Process(target=random_time)
    process_1.start()

    process_2 = Process(target=random_time)
    process_2.start()
