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
        self.m = 116
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

    #def str_to_MinHash(str1, q, seed=0):
     #   return min([mmh3.hash(str1[i:i + q], seed) for i in range(len(str1) - q + 1)])

    def intersection(self, lst1, lst2):
      lst3 = [value for value in lst1 if value in lst2]
      return lst3

    def string_to_ngram_set(self, str, q):
       return set([str[i:i+q] for i in range(len(str)-q+1)])

    def jaccard_set(self, set1, set2):
      # return Jaccard similarity coefficient between two sets
      isz = len(set1.intersection(set2))
      return  float(isz) / (len(set1) + len(set2) - isz)

    def jaccard(self, str1, str2, q):
       # turn two strings into sets, then return Jaccard similarity coefficient of those sets
       return  self.jaccard_set(self.string_to_ngram_set(str1, q), self.string_to_ngram_set(str2, q))


    def get(self, key):
        #key = "_" + key + "_"
        matchingKeys = {}
        results = []
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
                  arr = self.vs[key]["k"]
                  #print(hamming(r, arr)*len(arr), math.ceil((1 - self.t)*len(arr)))
                  dist = hamming(r, arr)*len(arr)
                  if dist <= math.ceil((1 - self.t)*len(arr)):
                      matchingKeys[key] = 1
                      results.append({key: self.vs[key]["v"]})
        return results


    def put(self, key, v):
        r = []
        #key = "_"+key+"_"
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


    def verify(self, key):
        results = self.get(key)
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





