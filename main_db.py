import DynaHash as DH
import time
import csv

def populate(dh):
    with open('names_small.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            author = row[0]
            year = row[1]
            dh.db_add(author, year)





if __name__ == '__main__':
    dh = DH.DynaHash(db=True, db_dir="./leveldb")

    populate(dh)

    with open('names_small.csv', newline='', encoding="utf8") as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         headers = next(reader)
         for row in reader:
                 author = row[0]
                 year = row[1]
                 results, no_items = dh.db_get(author)
                 print("KEY:", author)
                 print(results, no_items)
                 print("===========================================================")




