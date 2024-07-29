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
import numpy as np
import BKTree as BK
class DynaHash:

    def __init__(self, k=6, th=0.5, eps=0.1, delta=0.1, q=2, omega=0, db=False, db_dir=""):
        self.delta = delta
        self.eps = eps
        self.th = th
        self.k = k

        self.m = math.ceil(math.log(1/0.1)/(2*0.1**2))
        self.t = math.ceil((1 - self.th)*self.m)
        p = 1 - self.th
        self.L = math.ceil(math.log(self.delta) / math.log(1 - p**self.k))
        self.omega = omega
        s_omega = 0
        for i in range(omega + 1):
            s_omega += p ** (self.k - i)
        self.newL = math.ceil(math.log(self.delta) / math.log(1 - s_omega))
        if self.omega > 0:
            print("L_omega=", self.newL," hash tables used instead of L=",self.L, "m=", self.m)
        else:
            print("L=", self.L,  "m=", self.m)

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


    def finalize(self):
        self.trees = [BK.BKTree( iter(self.dictB[l].keys())  ) for l in range(self.L)]



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
               keys += str(r[s])+"_"
           keys = keys[:-1]

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
        queryTime = round(end - st, 4)
        return results, no_items, queryTime


    def get_ranks(self, key, th):
        matchingKeys = {}
        no_items = 0
        r = []
        for j in range(self.m):
             k = self.str_to_MinHash(key, 2, j)
             r.append(k)
        st = time.time()
        th0 = 0.95
        no_ranks = int((1- th)/0.05)
        #ranks = [[]]*no_ranks
        #print("no ranks=",no_ranks)
        bins = []
        for th00 in np.arange(0.95, th-0.05 , -0.05):
            t = math.ceil((1 - th00) * self.m)
            bins.append(t)
        ranks = [[] for _ in range(len(bins))]


        t = math.ceil((1 - th0) * self.m)
        L1 = 0
        while True:
          p = th0
          L2 = math.ceil(math.log(self.delta) / math.log(1 - p**self.k))
          #print("th0", th0, "L1=", L1, "L2=", L2, "t=",t)
          for l in range(L1, L2):
             sample = self.samples[l]
             keys = ""
             for s in sample:
                  keys += str(r[s]) + "_"
             keys = keys[:-1]

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
                        bin = np.digitize([dist], bins)
                        if bin[0] < len(ranks):
                           ranks[bin[0]].append({"k": k, "v": self.vs[k]["v"]})
                           #results.append({"k": k, "v": self.vs[k]["v"]})
                           #print("Found", k, self.vs[k]["v"], "d=",dist, "bin=",bin[0])

          #ranks.append(results)
          L1 = L2
          th0 = th0 - 0.05
          t = math.ceil((1 - th0) * self.m)
          if round(th0, 2) < round(th, 2):
              break

        end = time.time()
        query_time = round(end - st, 4)
        return ranks, no_items, query_time



    def probe_get(self, key):
        matchingKeys = {}
        results = []
        no_items = 0
        r = []
        for j in range(self.m):
             k = self.str_to_MinHash(key, 2, j)
             r.append(k)
        st = time.time()
        scanned_blocks = 0
        sum_blocks = 0
        avg_blocks = 0

        for l in range(self.newL):
           sample = self.samples[l]
           keys = ""
           for s in sample:
               keys += str(r[s]) +"_"
           keys = keys[:-1]

           kks = [keys]
           extra_keys = self.trees[l].find(keys, self.omega)
           for kk1 in extra_keys:
                if kk1 != keys:
                    kks.append(kk1)

           scanned_blocks += len(kks)
           #print(scanned_blocks, keys)
           sum_blocks +=  len(kks) + 1
           for keys in kks:
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


           if scanned_blocks >= self.newL:
                avg_blocks = sum_blocks / (l+1)
                #print("scanned_blocks reached L=", scanned_blocks, "current L=", l)
                break

        end = time.time()
        queryTime = round(end - st, 4)
        return results, no_items, queryTime, avg_blocks







    def add(self, key, v):
        r = []
        for j in range(self.m):
                k = self.str_to_MinHash(key, 2, j)
                r.append(k)
        for l in range(self.L):
           sample = self.samples[l]
           keys = ""
           for s in sample:
                keys += str(r[s])+"_"
           keys = keys[:-1]

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
                if not k1.startswith(ks):
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







