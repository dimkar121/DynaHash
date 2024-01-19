# DynaHash
DynaHash is a general purpose dictionary, or hashmap, or hashtable, which operates in an approximate manner upon the retrieval of its items. 
Speicifically for a key $k$, DynaHash retrieves all items whose keys are within a specified Hamming distance threshold from $k$. 
Τhe user specifies the desired sesnitivity in terms of Jaccard similarity and DynaHash calculates the corresponding Hamming distance threshold. 
For instance, the Jaccard $(\mathcal{J})$ similarities of the following pairs of strings, using their 2-grams, are: 
- $\mathcal{J}(\textit{William}, \textit{Will}) = 0.5$,  
- $\mathcal{J}(\textit{Dimitrios}, \textit{Dimitris}) = 0.666$,  
- $\mathcal{J}(\textit{Katerina}, \textit{Catherina}) = 0.5$.  

Each key is transformed into a MinHash sequence, and is then hashed using Hamming LSH.

DynaHash supports two main methods put() and get(); method `put()` inserts a key and its value into DynaHash, while `get()` returns a vector that contains all keys, and their values in terms of dictionaries, whose Hamming distances are within the specified Hamming distance threshold. 

```python
dh = new DynaHash(t=0.5)
dh.put("Katerina", v1)
dh.put("Cathrine", v2)
fh.get("Catherina") ---> [{"Katerina":v1}, {"Cathrine":v2}]
```

The storage requirements are $O(Ln)$ in the number $n$ of items, where $L$ denotes the number of the internal hash tables that are used.
The query time, although is data dependent, by tuning appropriately the parameters can be $O(\sqrt{n})$.



## Running the artifact
The source has been tested with Python version 3.12
- Clone the repo
- The `requirements.txt` file lists all Python modules that the source depends on. These modules can be installed using:
 ```
pip3 install -r requirements.txt
```
