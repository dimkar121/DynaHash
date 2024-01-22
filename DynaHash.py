import math
import mmh3
import random
import time
try:
    import plyvel
except ModuleNotFoundError:
    pass
import pickle
import os
class DynaHash:

    def __init__(self, k=6, th=0.5, eps=0.1, delta=0.1, q=2, db=False, db_dir=""):
        self.delta = delta
        self.eps = eps
        self.th = th
        self.k = k
        self.m = math.ceil(math.log(1/delta)/(2*eps**2))
        self.t = math.ceil((1 - self.th)*self.m)
        p = 1 - self.th
        self.L = math.ceil(math.log(self.delta) / math.log(1 - p**self.k))
        print("L=", self.L, "m=", self.m)
        self.q = q
        self.createSamples()
        self.dictB = [dict() for l in range(self.L)]
        self.vs = {}
        if db == True:
            self.db = True
            self.db1 = plyvel.DB(db_dir, create_if_missing=True)
            self.db2 = plyvel.DB(db_dir+"/objects/", create_if_missing=True)


    def Hamming(self, v1, v2):
       return sum([1 for i, j in zip(v1, v2) if i != j])



    def createSamples(self):
        self.samples = []
        if self.db == True:
            if os.path.exists(self.db_dir + '/objects/samples.pickle'):
                with open(self.db_dir + '/objects/samples.pickle', 'rb') as handle:
                    self.samples = pickle.load(handle)
                    return
        lm = list(range(self.m))
        for l in range(self.L):
             s = random.sample(lm, self.k)
             self.samples.append(s)
        if self.db == True:
            with open(self.db_dir+'/objects/samples.pickle', 'wb') as handle:
               pickle.dump(self.samples, handle, protocol=pickle.HIGHEST_PROTOCOL)


    def str_to_MinHash(self, str1, q, seed=0):
        return min([mmh3.hash(str1[i:i + q], seed) for i in range(len(str1) - q + 1)])



    def get(self, key):
        matchingKeys = {}
        results = []
        no_items = 0
        r = []
        for j in range(self.m):
             k = self.str_to_MinHash(key, 2, j)
             r.append(k)
        for l in range(self.L):
           sample = self.samples[l]
           keys = ""
           for s in sample:
               keys += str(r[s])
           if keys in self.dictB[l]:
              key_list = self.dictB[l][keys]
              for k in key_list:
                  if k in matchingKeys.keys():
                     continue
                  no_items += 1
                  arr = self.vs[k]["k"]
                  dist = self.Hamming(r, arr)
                  if dist <= self.t:
                      matchingKeys[k] = 1
                      results.append({k: self.vs[k]["v"]})
        return results, no_items


    def add(self, key, v):
        r = []
        for j in range(self.m):
             k = self.str_to_MinHash(key, 2, j)
             r.append(k)
        for l in range(self.L):
           sample = self.samples[l]
           keys = ""
           for s in sample:
               keys += str(r[s])
           if keys in self.dictB[l]:
                data = self.dictB[l][keys]
                self.vs[key] = {"v": v, "k": r}
                data.append(key)
           else:
                self.vs[key] = {"v": v, "k": r}
                self.dictB[l][keys] = [key]


    def get_items_no(self):
        return len(self.vs.keys())



    def get_ground_truth(self, key):
        results, no_items = self.get(key)
        ground_truth = []
        r = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)
        for k in self.vs.keys():
            arr = self.vs[k]["k"]
            dist = self.Hamming(r, arr)
            if dist <= self.t:
                 ground_truth.append(k)

        return ground_truth

    def db_add(self, key, v):
        r = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)

        for l in range(self.L):
            sample = self.samples[l]
            keys = ""
            for s in sample:
                keys += str(r[s])
            ts = time.time()
            k = "".join([str(l), ":", keys, "!", str(ts)])
            k = bytes(k, 'utf-8')
            self.db1.put(k, key)
            bKey = bytes(key, 'utf-8')
            self.db2.put(bKey, {"v": v, "k": r})


    def db_get(self, key):
        results = []
        r = []
        no_items = 0
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)
        matchingKeys = {}
        for l in range(self.L):
            sample = self.samples[l]
            keyArr = []
            keys= ""
            for s in sample:
                keys += str(r[s])
                keyArr.append(str(r[s]))
            k = "".join([str(l), ":", keys])
            k = bytes(k, "utf-8")
            for _, k in self.db1.iterator(prefix=key):
                k = bytes.decode(k, 'utf-8')
                if k in matchingKeys.keys():
                    continue
                no_items += 1
                arr = []
                for j in range(self.m):
                    k1 = self.str_to_MinHash(k, 2, j)
                    arr.append(k1)
                r = self.db2.get(key)
                dist = self.Hamming(r["k"], arr)
                if dist <= self.t:
                    matchingKeys[key] = 1
                    results.append({key: self.db2.get(key)["v"]})

        return  results, no_items



