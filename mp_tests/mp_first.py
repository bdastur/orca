#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time


def printFunction(queue, continent="Asia"):
    print("Name is: ", continent)
    time.sleep(1)
    print("Done sleeping: ", continent)
    if queue is not None:
        while not queue.empty():
            print("Item in queue: ", queue.get(), " continent: ", continent)


def main():
    print("Number of CPUs: ", multiprocessing.cpu_count())
    names = ["America", "Europe", "Africa", "Japan", "INdia", "France", "Berlin", "Fremont", "Indonesia", "Tiwan", "Shanghai", "Orlando", "Jackson"]
    procs = []
    proc = multiprocessing.Process(target=printFunction, args=(None,))
    procs.append(proc)
    proc.start()

    pQueue = multiprocessing.Queue()
    pQueue.put("test0")

    for name in names:
        proc = multiprocessing.Process(target=printFunction, args=(pQueue, name,),)
        procs.append(proc)
        proc.start()

    pQueue.put("test1")

    for proc in procs:
        proc.join()



if __name__ == '__main__':
    main()
