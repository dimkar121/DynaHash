import DynaHash as DH
import time
import csv




def populate(dh):
    with open('./data/names_small.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            author = row[0]
            year = row[1]
            dh.db_add(author, year)





if __name__ == '__main__':
    dh = DH.DynaHash(db=True, db_dir="./data_db")

    populate(dh)

    i = 0
    recalls = 0
    precisions = 0
    sum_items = 0
    sum_query_time = 0
    with open('./data/names_small.csv', newline='', encoding="utf8") as csvfile:
         reader = csv.reader(csvfile, delimiter=';')
         headers = next(reader)
         for row in reader:
                 author = row[0]
                 year = row[1]
                 results, no_items, query_time = dh.db_get(author)
                 print("KEY:", author)
                 print(results, no_items)
                 print("===========================================================")
                 sum_items += no_items
                 sum_query_time += query_time
                 ground_truth = dh.get_db_ground_truth(author)
                 tp = 0
                 fp = 0
                 if len(ground_truth) > 0:
                     i += 1
                     for r in results:
                         key = r["k"]
                         if key in ground_truth:
                             tp += 1
                         else:
                            fp += 1
                     recalls += tp / len(ground_truth)
                     precisions += tp / (tp + fp)

         print("Avg recall", round(recalls / i, 2))
         print("Avg precision", round(precisions / i, 2))
         print("Avg query time (Avg number of items processed)", round(sum_items / i, 2))
         print("Avg query time", round(sum_query_time / i, 4))




