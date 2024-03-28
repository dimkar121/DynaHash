import DynaHash as DH
import time
import csv

if __name__ == '__main__':
    dh = DH.DynaHash()

    start = time.time()
    i = 0
    with open('./data/names_small.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            try:
                author = row[0]
                year = row[1]
                dh.add(author, year)
            except:
                continue
    end = time.time()
    print("blocking time=", end - start)

    rs = 0
    sum_items = 0
    ps = 0
    i = 0
    for k in dh.vs.keys():
        results, no_items, queryTime = dh.get(k)
        print("KEY:", k)
        print(results, no_items, queryTime)
        print("===========================================================")
        sum_items += no_items
        ground_truth = dh.get_ground_truth(k)
        tp = 0
        fp = 0
        if len(ground_truth) > 0:
            i += 1
            for r in results:
                key = r["k"]
                if key in ground_truth:
                    tp += 1
                else:
                    fp += 1
            rs += tp / len(ground_truth)
            ps += tp / (tp + fp)

    print("Avg recall", round(rs / i, 2))
    print("Avg precision", round(ps / i, 2))
    print("Avg query time (Avg number of items processed)", round(sum_items / i, 2))

