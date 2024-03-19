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

    i = 0
    recalls = 0
    precisions = 0
    sum_items = 0
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
                 ground_truth = dh.get_db_ground_truth(author)
                 tp = 0
                 fp = 0
                 if len(ground_truth) > 0:
                     i += 1
                     sum_items += no_items
                     for r in results:
                         key = list(r.keys())[0]
                         if key in ground_truth:
                             tp += 1
                         else:
                            fp += 1
                         recalls += tp / len(ground_truth)
                         precisions += tp / (tp + fp)

         print("Avg recall", recalls / i)
         print("Avg precision", precisions / i)
         print("Avg query time (Avg number of items processed)", sum_items / i)




