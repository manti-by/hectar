import random
from threading import Thread, get_ident
from time import sleep


def threaded_function():
    for _ in range(10):
        print(f"From thread: {get_ident()}")
        sleep(random.randint(1, 3))


if __name__ == "__main__":
    thread_1 = Thread(target=threaded_function)
    thread_1.start()

    thread_2 = Thread(target=threaded_function)
    thread_2.start()
