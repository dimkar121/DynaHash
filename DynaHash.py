import math
import mmh3
import random
import time
import json
try:
    import rocksdbpy
    from rocksdbpy import Option
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

        self.m = math.ceil(math.log(1/0.1)/(2*0.1**2))
        self.t = math.ceil((1 - self.th)*self.m)
        p = 1 - self.th
        self.L = math.ceil(math.log(self.delta) / math.log(1 - p**self.k))
        print("L=", self.L, "m=", self.m)
        self.q = q
        self.db = False
        if db == True:
            self.db = True
            self.db_dir = db_dir
            opts = Option()
            opts.create_if_missing(True)
            opts.set_max_open_files(1000)
            self.db1 = rocksdbpy.open(db_dir, opts)
            self.db2 = rocksdbpy.open(db_dir+'/objects/', opts)
        self.createSamples()
        self.dictB = [dict() for l in range(self.L)]
        self.vs = {}



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
        st = time.time()
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
                  arr = self.vs[k]["h"]
                  dist = self.Hamming(r, arr)
                  if dist <= self.t:
                      matchingKeys[k] = 1
                      results.append({"k": k, "v": self.vs[k]["v"]})
        end = time.time()
        queryTime = round(end - st, 2)
        return results, no_items, queryTime


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
                self.vs[key] = {"v": v, "h": r}
                data.append(key)
           else:
                self.vs[key] = {"v": v, "h": r}
                self.dictB[l][keys] = [key]


    def get_items_no(self):
        return len(self.vs.keys())



    def get_ground_truth(self, key):
        ground_truth = []
        r = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)
        for k in self.vs.keys():
            arr = self.vs[k]["h"]
            dist = self.Hamming(r, arr)
            if dist <= self.t:
                 ground_truth.append(k)

        return ground_truth

    def get_db_ground_truth(self, key):
        k = bytes(key, "utf-8")
        ground_truth = []
        m_key = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            m_key.append(k)

        for k, v in self.db2.iterator():
            dict_obj = bytes.decode(v, 'utf-8')
            dict_obj = json.loads(dict_obj)
            dist = self.Hamming(m_key, dict_obj["h"])
            if dist <= self.t:
                 k1 = bytes.decode(k, 'utf-8')
                 ground_truth.append(k1)

        return ground_truth



    def db_get(self, key):
        results = []
        m_key = []
        no_items = 0
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            m_key.append(k)
        matchingKeys = {}
        st = time.time()
        for l in range(self.L):
            sample = self.samples[l]
            keys = ""
            for s in sample:
                keys += str(m_key[s])
            ks = "".join([str(l), ":", keys])
            bkey = bytes(ks, "utf-8")
            for k, v in self.db1.iterator(mode="from", key=bkey):
                k1 = bytes.decode(k, 'utf-8')
                if not k1.startswith(key):
                    break
                v1 = bytes.decode(v, 'utf-8')
                if v1 in matchingKeys.keys():
                    continue
                no_items += 1
                arr = []
                dict_obj = self.db2.get(v)
                dict_obj = bytes.decode(dict_obj, 'utf-8')
                dict_obj = json.loads(dict_obj)
                dist = self.Hamming(m_key, dict_obj["h"])
                if dist <= self.t:
                    matchingKeys[v1] = 1
                    results.append({"k": v1, "v": dict_obj["v"]})
        end = time.time()
        queryTime = round(end - st, 2)
        return results, no_items, queryTime

    def db_add(self, key, v):
        r = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)
        bKey = bytes(key, 'utf-8')
        b_dict = json.dumps({"v": v, "h": r}, indent=2).encode('utf-8')
        self.db2.set(bKey, b_dict)

        for l in range(self.L):
            sample = self.samples[l]
            keys = ""
            for s in sample:
                keys += str(r[s])
            ts = time.time()
            k = "".join([str(l), ":", keys, "!", str(ts)])
            k = bytes(k, 'utf-8')
            self.db1.set(k, bKey)







