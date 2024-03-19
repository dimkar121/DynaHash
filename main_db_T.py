import DynaHash as DH
import time
import csv
import random
import math
from datetime import datetime

t = 0.5
k = 6
kf = 4
w = 1000
p = 1 - t
Lf = math.ceil(math.log(0.1) / math.log(1 - p ** kf))

T = []
for l in range(Lf):
    T.append(dict())
    T[l]["_evictions"] = 0


def populate(dh):
    with open('2023.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        #headers = next(reader)
        for row in reader:
            author = row[0]
            dh.db_add(author, "2023")






def query(dh, q):
      global kf, Lf, w, T, t, m
      now = datetime.now()
      dts = now.strftime("%d/%m/%Y %H:%M:%S")

      noRecs = 0
      i = 1
      L, samples = dh.createSamples(t, m, 6, 1)
      matchingNames = {}
      r = []
      for j in range(m):
         k = dh.str_to_MinHash(q, 2, j)
         r.append(k)
      st = time.time()

      authors = []
      for l in range(Lf):
         sample = samples[l]
         key = ""
         keyArr = []
         for s in  sample[0:kf]:
            key += str(r[s])
            keyArr.append(str(r[s]))

         if key in T[l]:
            vs = T[l][key]
            for name in vs:
               if name in matchingNames.keys():
                   continue
               noRecs += 1
               arr = []
               for j in range(m):
                    k1 = dh.str_to_MinHash(name, 2, j)
                    arr.append(k1)

               dist = dh.hamming(r, arr)
               if dist <= t:
                   matchingNames[name] = 1
                   authors.append(name)
                   i+=1

      end = time.time()
      queryTime = round(end - st, 2)
      return authors, noRecs, queryTime

















if __name__ == '__main__':
    dh = DH.DynaHash(db=True, db_dir="./leveldb")
    populate(dh)

    i = 0
    sum_items = 0
    with open('2023.csv', newline='', encoding="utf8") as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         #headers = next(reader)
         for row in reader:
             try:
               author = row[0]
               i += 1
               if i == 100000:
                      break
               r = []
               for j in range(m):
                  k = dh.str_to_MinHash(author, 2, j)
                  r.append(k)
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
         with open('/home/dimkar/data/dblp/2023.csv', newline='') as csvfile:
             reader = csv.reader(csvfile, delimiter=';')
             for row in reader:
                author = row[0]
                i += 1
                if i == 100:
                  break
                authors, noRecs, queryTime = dh.db_get(author)
                print("-" * 30)
                print("query time=", queryTime, "number of records retrieved and evaluated=", noRecs, "number of matches=",  len(authors))
                authors, noRecs, queryTime = query(author)
                print("query time=", queryTime, "number of records retrieved and evaluated=", noRecs, "number of matches=",  len(authors))
                print("-" * 30)




