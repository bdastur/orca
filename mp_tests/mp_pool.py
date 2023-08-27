#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing
import time


def worker(workData):
    print("Processing %s waiting for %s seconds" % (workData[0], workData[1]))
    time.sleep(workData[1])
    print("Finished %s" % workData[0])
    result = {}
    result["workItem"] = workData[0]
    result["result"] = workData[1] * 4
    return result


def applyWorker(data):
    print("Apply worker data %s" % data)
    time.sleep(2)
    print("Worker %s done!" % data)

    return data


def initThread():
    print("Init thread")


def mpSampleOne():
    work = (["A", 5], ["B", 3], ["C", 4], ["D", 2], ["E", 2], ["F", 1], ["G", 2], ["H", 6], ["I", 3],)

    with multiprocessing.Pool(3) as pool:
        for result in pool.map(worker, work):
            print("Result: ", result)

    print("Done")


def mpSampleTwo():
    work = (["A", 5], ["B", 3], ["C", 4], ["D", 2], ["E", 2], ["F", 1], ["G", 2])

    pool = multiprocessing.Pool(5)
    result = pool.map(worker, work)
    print(result)
    pool.close()


def mpSampleThree():
    work = (["A", 5], ["B", 3], ["C", 4], ["D", 2], ["E", 2], ["F", 1], ["G", 2],)
    print(work[0])
    pool = multiprocessing.Pool(3)
    result = pool.apply(applyWorker, args=(work[0],))
    print("result: ", result)
    pool.close()
    

def mpSampleAsyncOne():
    work = ["A", 5]
    pool = multiprocessing.Pool(2)
    result = pool.apply_async(applyWorker, args=(work,))
    value = result.get()
    print("Result: ", value)


def mpSampleAsyncTwo():
    work = (["A", 5], ["B", 3], ["C", 4], ["D", 2], ["E", 2], ["F", 1], ["G", 2])

    pool = multiprocessing.Pool(3)
    result = pool.map_async(worker, work)

    for value in result.get():
        print("Result: ", value)
    pool.close()


def main():
    #mpSampleOne()
    #print("Sample Two =====")
    #mpSampleTwo()
    #print("Sample Three =====")
    #mpSampleThree()
    #print("Sample Four =====")
    #mpSampleAsyncOne()
    print("Sample Five =====")
    mpSampleAsyncTwo()


if __name__ == '__main__':
    main()
