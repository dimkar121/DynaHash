import DynaHash as DH
import time
import csv
import math

if __name__ == '__main__':
    dh = DH.DynaHash()

    start = time.time()
    i = 0
    with open('names.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            try:
                author = row[0]
                year = row[1]
                dh.put(author, year)
                i += 1
            except:
                continue
    end = time.time()
    print("time=", end - start)

    rs = 0
    sum_items = 0
    ps = 0
    i = 0
    for k in dh.vs.keys():
        results, no_items = dh.get(k)
        sum_items += no_items
        print(no_items, math.sqrt(dh.get_items_no()))
        ground_truth = dh.verify(k)
        tp = 0
        fp = 0
        if len(ground_truth) > 0:
            i += 1
            for r in results:
                key = list(r.keys())[0]
                if key in ground_truth:
                    tp += 1
                else:
                    fp += 1
            rs += tp / len(ground_truth)
            ps += tp / (tp + fp)

    print("AVG RECALL", rs / i)
    print("AVG PRECISION", ps / i)
    print("AVG TIME", sum_items / i)

