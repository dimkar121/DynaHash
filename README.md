# DynaHash
DynaHash is a general purpose dictionary, or hashmap, or hashtable, which operates in an approximate manner upon the retrieval of its items. 
Speicifically for a key $k$, DynaHash retrieves all items whose keys are within a specified Hamming distance threshold. 
Each key is transformed into a MinHash sequence, and is then hashed using Hamming LSH.
The storage requirements are $O(Ln)$ in the number $n$ of items, where $L$ denotes the number of the internal hash tables that are used.
The query time, although is data dependent, by tuning appropriately the parameters can be $O(\sqrt{n})$.



## Running the artifact
The source has been tested with Python version 3.12
- Clone the repo
- The `requirements.txt` file lists all Python modules that the source depends on. These modules can be installed using:
  `pip3 install -r requirements.txt`.
