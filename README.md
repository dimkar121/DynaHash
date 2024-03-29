# DynaHash
DynaHash is a general purpose dictionary, or hashmap, or hashtable, which operates in an approximate manner upon its matching function of keys. 
Speicifically for a query key, DynaHash retrieves all items, whose keys are within a specified Hamming distance threshold from that query key. 
Τhe user specifies the desired sesnitivity in terms of Jaccard similarity and DynaHash calculates the corresponding Hamming distance threshold. 
For instance, the Jaccard $(\mathcal{J})$ similarities of the following pairs of strings, using their 2-grams, are: 
- $\mathcal{J}(\textit{William}, \textit{Will}) = 0.5$,  
- $\mathcal{J}(\textit{Dimitrios}, \textit{Dimitris}) = 0.666$,  
- $\mathcal{J}(\textit{Katerina}, \textit{Catherina}) = 0.5$.  

Each key is converted into a MinHash sequence, which is then hashed using Hamming LSH.

DynaHash supports two main methods `add()` and `get()`; method `add(k, o)` inserts a key $k$ and its object $o$ into DynaHash, while `get(k)` returns a vector that contains all items, in terms of dictionaries, whose keys are within the Hamming distance threshold, which has been calculated using the specified sensitivity, from $k$. The default sensitivity has been set to $0.5$.  

```python
>>> import DynaHash as DH
>>> dh = DH.DynaHash()
>>> dh.add("Staci", object())
>>> dh.add("Stacie", object())
>>> dh.get("Stacy")
([{'Staci': <object object at 0x00000184757D1220>}, {'Stacie': <object object at 0x00000184757D1820>}], 2)
```
It also returns the total number of items that have been retrieved to process a query record. The number $L$ of the hash tables that are required depends on parameters $t$, $k$, and $\delta$, which are the Jaccard similarity, the number of components that will be randomly and uniformly selected from each MinHash sequence, and the failure probability, respectively. 

There are two CSV files for testing `names_small.csv` and `names_large.csv`. The former contains $2,209$ names, while the latter includes all unique author names ($\approx 1,800,000$) from DBLP in the year 2014.
Using an ESXi U2 VM with 8 cores and 48GB of main memeory, it takes almost $2,000$ seconds to build the indexing structure that contains all names of `names_large.csv`. For resolving a query, the average clock time is $0.02$ seconds, while the average number of the retrieved items  is $1,1139$, which is $\approx \sqrt{1,800,000}$. 

There is also a DB version of DynaHash, which is backed by [levelDB](https://github.com/google/leveldb) for the persistent operations. [Plyvel](https://github.com/wbolster/plyvel) is The Python wrapper on top of levelDB. The main funcions are `db_add(k, o)` and `db_get(k)`. Any serializable JSON object $o$ can be the value of a key $k$.


The storage requirements are $O(Ln)$ in the number $n$ of items, where $L$ denotes the number of the internal hash tables that are being used.
The query time, by tuning properly the parameters $t$ and $s$, is $\Theta(\sqrt{n})$.



## Running the artifact
The source has been tested with Python version 3.12
- Clone the repo
- `main.py` and `main_db.py` showcase the operations of the pure in-memory version and the DB version,respectively.  
- The `requirements.txt` file lists all Python modules that the source depends on. These modules can be installed using:
 ```
pip3 install -r requirements.txt
```
