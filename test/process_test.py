from multiprocessing import Process, Queue, cpu_count
import queue
import random
import time




def work(id, queue):
    while True:
        task = queue.get()
        if task is None:
            break
        time.sleep(0.05)
        print("%d task:" % id, task)
    queue.put(None)


class Manager:
    def __init__(self):
        self.queue = Queue()
        self.NUMBER_OF_PROCESSES = 4

    def start(self):
        print("starting %d workers" % self.NUMBER_OF_PROCESSES)
        self.workers = [Process(target=work, args=(i, self.queue,))
                        for i in range(self.NUMBER_OF_PROCESSES)]
        for w in self.workers:
            w.start()



    def stop(self):
        self.queue.put(None)
        for i in range(self.NUMBER_OF_PROCESSES):
            self.workers[i].join()
        self.queue.close()

if __name__ == '__main__':
    Manager().start()


import multiprocessing as mp
from multiprocessing import Queue

def foo(q):
    print(q)



if __name__ == '__main__':
    pool = mp.Pool()
    q = Queue()

    pool.map(foo, (q,))