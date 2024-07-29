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
    sum_query_time = 0
    ps = 0
    i = 0
    for k in dh.vs.keys():
        ranks, no_items, query_time = dh.get_ranks(k, 0.85)
        print("KEY:", k)
        print(ranks)
        print("===========================================================")
        sum_items += no_items
        sum_query_time += query_time
