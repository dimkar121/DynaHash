import DynaHash as DH
import time
import csv
import random
import math
from datetime import datetime

m = 116
kf = 4
w = 1000
t = 0.5
p = 1 - t
Lf = math.ceil(math.log(0.1) / math.log(1 - p ** kf))

T = []
for l in range(Lf):
    T.append(dict())
    T[l]["_evictions"] = 0

A = {}

def query(dh, q):
    global kf, Lf, w, T, t, m

    noRecs = 0
    i = 1
    matchingNames = {}
    r = []
    for j in range(m):
        k = dh.str_to_MinHash(q, 2, j)
        r.append(k)
    st = time.time()

    authors = []
    for l in range(Lf):
        sample = dh.samples[l]
        key = ""
        keyArr = []
        for s in sample[0:kf]:
            key += str(r[s])
            keyArr.append(str(r[s]))

        if key in T[l]:
            vs = T[l][key]
            for name in vs:
                if name in matchingNames.keys():
                    continue
                noRecs += 1

                arr = A[name]["h"]
                dist = dh.Hamming(r, arr)
                if dist <= dh.t:
                    matchingNames[name] = 1
                    authors.append(name)
                    i += 1

    end = time.time()
    queryTime = round(end - st, 2)
    return authors, noRecs, queryTime


if __name__ == '__main__':
    dh = DH.DynaHash(db=True, db_dir="./data_T")
    print("T k_\phi=", kf, "L_\phi=", Lf)
    i = 0
    sum_items = 0
    with open('2023.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            try:
                author = row[0]
                year = row[1]
                i += 1
                if i % 10000 == 0:
                    print(i)
                dh.db_add(author, year)
                r = []
                for j in range(m):
                    k = dh.str_to_MinHash(author, 2, j)
                    r.append(k)
                A[author] = {"v": year,  "h": r}
                for l in range(Lf):
                    sample = dh.samples[l]
                    key = ""
                    keyArr = []
                    for s in sample[0:kf]:
                        key += str(r[s])
                        keyArr.append(str(r[s]))
                    if key in T[l]:
                        if len(T[l][key]) == w:
                            vs = T[l][key]
                            rnd = random.randint(0, w - 1)
                            vs[rnd] = author
                            T[l]["_evictions"] += 1
                        else:
                            vs = T[l][key]
                            vs.append(author)

                    else:
                        T[l][key] = [author]
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)

        i = 0
        with open('2023.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                author = row[0]
                i += 1
                if i == 100:
                    break
                authors, noRecs, queryTime = dh.db_get(author)
                print("-" * 30)
                print("author", author)
                print("DB number of records retrieved and evaluated=", noRecs, "number of matches=", len(authors), "clock time=", queryTime)
                authors, noRecs, queryTime = query(dh, author)
                print("T number of records retrieved and evaluated=", noRecs, "number of matches=", len(authors), "clock time=", queryTime)
                print("-" * 30)




