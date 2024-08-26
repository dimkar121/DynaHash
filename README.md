# DynaHash

This is the accompanying artifact for the manuscript "DynaHash: An Efficient Blocking Mechanism for Streaming Record Linkage" co-authored by D. Karapiperis (IHU), C. Tjortjis (IHU), and V.S. Verykios (HOU).
## Abstract
Record linkage holds a crucial position in data management and analysis by identifying and merging records from disparate data sets that pertain to the same real-world entity. As data volumes grow, the intricacies of record linkage amplify, presenting challenges, such as potential redundancies and computational complexities. This paper introduces DynaHash, a novel randomized record linkage mechanism that utilizes (a) the MinHash technique to generate compact representations of blocking keys and (b) Hamming Locality-Sensitive Hashing to construct the blocking structure from these vectors. By employing these methods, DynaHash offers theoretical guarantees of accuracy and achieves sublinear runtime complexities, with appropriate parameter tuning. It comprises two key components: a persistent storage system for permanently storing the blocking structure to ensure complete results, and an in-memory component for generating very fast partial results by summarizing the persisted blocking structure. Our experimental evaluation against three state-of-the-art methods on six real-world data sets demonstrate DynaHash's exceptional recall rates and query times, which are at least 2x faster than its competitors and do not depend on the size of the underlying data sets.

## Description

DynaHash is a general purpose dictionary, or hash map, or hash table, which operates in an approximate manner upon its matching function of keys. 
<!-- Speicifically for a query key, DynaHash retrieves all items, whose similarity of their keys meets a user-specified Jaccard threshold with a certain probability bound. 
For instance, the Jaccard $(\mathcal{J})$ similarities of the following pairs of strings, using their sets of 2-grams, are: 
- $\mathcal{J}(\textit{William}, \textit{Will}) = 0.5$,  
- $\mathcal{J}(\textit{Dimitrios}, \textit{Dimitris}) = 0.666$,  
- $\mathcal{J}(\textit{Katerina}, \textit{Catherina}) = 0.5$.  -->

Each key is converted into a MinHash [1] vector, using the method introduced in [2], which is, then, blocked using Hamming LSH [3].

DynaHash supports two main methods `add()` and `get()`; method `add(k, o)` inserts a key $k$ and its object $o$ into DynaHash, while `get(k)` returns a list that contains all the similar items that have been found in the Hamming space with a probability at least $1-\delta$ for some user-defined $\delta$.
```python
>>> import DynaHash as DH
>>> dh = DH.DynaHash()
>>> dh.add("Staci", object())
>>> dh.add("Stacie", object())
>>> dh.get("Stacy")
([{'k':'Staci', 'v':<object object at 0x00000184757D1220>}, {'k':'Stacie', 'v':<object object at 0x00000184757D1820>}], 2)
```

There are two CSV files for testing `names_small.csv` and `names_large.csv`. The former contains $2,209$ names, while the latter includes all unique author names ($\approx 1,800,000$) from DBLP in the year 2014.
Using `names_large.csv`, the average clock-time for resolving a query is $0.38$ seconds using a ESXi U2 VM with 8 cores and 48GB of main memory. The average number of the retrieved items is $1,1139$ which is $\approx \sqrt{1,800,000}$. 

DynaHash is backed by Facebook's [RocksDB](https://github.com/facebook/rocksdb) for realizing its persistent operations. [Rocksdbpy](https://github.com/trK54Ylmz/rocksdb-py) is the Python wrapper used on top of RocksDB. The main funcions are `db_add(k, o)` and `db_get(k)`. Any serializable JSON object can be passed as object $o$ for a key $k$.

The storage requirements are $O(Ln)$ in the number $n$ of items, where $L$, which is a function of the parameters specified, denotes the number of the internal hash tables that are being used.
The query time, by tuning properly the parameters, is $\Theta(\sqrt{n})$.



## Running the artifact
Clone the repo and install project's dependencies:
```
pip3 install -r requirements.txt
```
The source has been tested with Python versions 3.10 and 3.12


The project includes several scripts which demonstrate specific operations:
- `main.py` and `main_db.py`: pure in-memory and DB operations, respectively.
- `main_db_T.py`: both the in-memory and persistent operations.
- `main_probe.py`: the multi-probe operation.
- `main_ranks.py`: the ranking operation of the results by adjusting the Jaccard threshold.
  
The following scripts evaluate the performance of DynaHash:
- `main_ACM_DBLP.py` uses the paired data sets ACM and DBLP to perform linkage.
- `main_Scholar_DBLP.py` uses the paired data sets Google Scholar and DBLP to perform linkage.
   
## References
- [1] A. Z. Broder, M. Charikar, A. Frieze, and M. Mitzenmacher. Minwise Independent Permutations. ACM STOC. 1998. 327–336.
- [2] D. Karapiperis, C. Tjortjis, and V.S. Verykios. 2024. A Suite of Efficient Randomized Algorithms for Streaming Record Linkage. IEEE TKDE, preprints, 2024. 
- [3] D. Karapiperis and V.S. Verykios. 2015. An LSH-based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage. IEEE TKDE 27, 4. 2015. 909–921.
