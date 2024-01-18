import math
import mmh3
from scipy.spatial.distance import hamming
import random

class DynaHash:

    def __init__(self, k=6, t=0.5, eps=0.1, delta=0.1, q=2):
        self.delta = delta
        self.eps = eps
        self.t = t
        self.k = k
        self.m = math.ceil(math.log(1/delta)/(2*eps**2))
        p = 1 - t
        L = math.ceil(math.log(self.delta) / math.log(1 - p**k))
        self.L = int(L)
        print("L=", self.L, "m=", self.m)
        self.q = q
        self.createSamples()
        self.dictB = [dict() for l in range(self.L)]
        self.vs = {}

    def createSamples(self):
        self.samples = []
        lm = list(range(self.m))
        for l in range(self.L):
             s = random.sample(lm, self.k)
             self.samples.append(s)
        #with open('/home/dimkar/leveldb/dblp/samples.pickle', 'wb') as handle:  # samples5.pickle k=5
           #pickle.dump(samples, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #with open('/home/dimkar/leveldb/dblp/samples.pickle', 'rb') as handle:
          #samples = pickle.load(handle)

    def str_to_MinHash(self, str1, q, seed=0):
        return min([mmh3.hash(str1[i:i + q], seed) for i in range(len(str1) - q + 1)])

    def string_to_ngram_set(self, str, q):
       return set([str[i:i+q] for i in range(len(str)-q+1)])



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
              for key in key_list:
                  if key in matchingKeys.keys():
                     continue
                  no_items += 1
                  arr = self.vs[key]["k"]
                  dist = hamming(r, arr)*len(arr)
                  if dist <= math.ceil((1 - self.t)*len(arr)):
                      matchingKeys[key] = 1
                      results.append({key: self.vs[key]["v"]})
        return (results, no_items)


    def put(self, key, v):
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



    def verify(self, key):
        results, no_items = self.get(key)
        ground_truth = []
        r = []
        for j in range(self.m):
            k = self.str_to_MinHash(key, 2, j)
            r.append(k)
        for k in self.vs.keys():
            arr = self.vs[k]["k"]
            dist = hamming(r, arr) * len(arr)
            if dist <= math.ceil((1 - self.t) * len(arr)):
                 ground_truth.append(k)

        tp = 0
        fp = 0
        if len(ground_truth) > 0:
             for result in results:
                key = list(result.keys())[0]
                if key in ground_truth:
                     tp += 1
                else:
                      fp += 1
             recall = tp / len(ground_truth)
             precision = tp / (tp + fp)
             print(key, "recall=", recall, "precision=", precision)
        return ground_truth





