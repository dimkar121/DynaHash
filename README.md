# DynaHash
DynaHash is a general purpose dictionary, or hashmap, or hashtable, which operates in an approximate manner upon its matching function of keys. 
Speicifically for a query key, DynaHash retrieves all items, whose similarity of their keys meet a user-specified Jaccard threshold. 
For instance, the Jaccard $(\mathcal{J})$ similarities of the following pairs of strings, using their sets of 2-grams, are: 
- $\mathcal{J}(\textit{William}, \textit{Will}) = 0.5$,  
- $\mathcal{J}(\textit{Dimitrios}, \textit{Dimitris}) = 0.666$,  
- $\mathcal{J}(\textit{Katerina}, \textit{Catherina}) = 0.5$.  

Each key is converted into a MinHash [1] vector, which is then blocked using Hamming LSH [2].

DynaHash supports two main methods `add()` and `get()`; method `add(k, o)` inserts a key $k$ and its object $o$ into DynaHash, while `get(k)` returns a list that contains all the similar items that have been found with a probability at least $1-\delta$ for some user-defined $\delta$.
```python
>>> import DynaHash as DH
>>> dh = DH.DynaHash()
>>> dh.add("Staci", object())
>>> dh.add("Stacie", object())
>>> dh.get("Stacy")
([{'k':'Staci', 'v':<object object at 0x00000184757D1220>}, {'k':'Stacie', 'v':<object object at 0x00000184757D1820>}], 2)
```

There are two CSV files for testing `names_small.csv` and `names_large.csv`. The former contains $2,209$ names, while the latter includes all unique author names ($\approx 1,800,000$) from DBLP in the year 2014.
For resolving a query, the average clock time is $0.01$ seconds using a ESXi U2 VM with 8 cores and 48GB of main memory. The average number of the retrieved items is $1,1139$ which is $\approx \sqrt{1,800,000}$. 

DynaHash is backed by Facebook's [RocksDB](https://github.com/facebook/rocksdb) for realizing its persistent operations. [Rocksdbpy](https://github.com/trK54Ylmz/rocksdb-py) is The Python wrapper which operates on top of RocksDB. The main funcions are `db_add(k, o)` and `db_get(k)`. Any serializable JSON object can be passed as object $o$ for a key $k$.

The storage requirements are $O(Ln)$ in the number $n$ of items, where $L$, which is a function of the parameters specified, denotes the number of the internal hash tables that are being used.
The query time, by tuning properly the parameters, is $\Theta(\sqrt{n})$.



## Running the artifact
The source has been tested with Python version 3.12
- Clone the repo
- `main.py` and `main_db.py` showcase the operations of the pure in-memory version and the DB version,respectively.  
- The `requirements.txt` file lists all Python modules that the source depends on. These modules can be installed using:
 ```
pip3 install -r requirements.txt
```
## References
- [1] A. Z. Broder, M. Charikar, A. Frieze, and M. Mitzenmacher. Minwise Independent Permutations. ACM STOC. 1998. 327–336.
- [2] D. Karapiperis and V.S. Verykios. 2015. An LSH-based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage. IEEE TKDE 27, 4. 2015. 909–921.
