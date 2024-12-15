import DynaHash as DH
import time
import csv

if __name__ == '__main__':
    dh = DH.DynaHash()

    start = time.time()
    i = 0
    with open('./data/names_large.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            try:
                author = row[0]
                year = row[1]
                v = dh.vectorize(author)
                i+=1
                if i % 100000 == 0:
                    print(i)
            except:
                continue
    end = time.time()
    print("Vectorization time=", end - start, "for", i, "records")
    print("Avg time", (end - start)/i, "seconds")