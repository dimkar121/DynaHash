import DynaHash as DH
import time
import csv

if __name__ == '__main__':
    dh = DH.DynaHash()
    data1 = {"Bruce Dickinson": "Bruce Dickinson Rec", "Steve Harris": "Steve harris Rec",
             "David Murray": "David Murray Rec", "Bruno Dickinson": "Bruno Dickinson Rec",
             "Steven Harris": "Steven Harris Rec"}

    for k in data1.keys():
        dh.put(k, data1[k])

    for k in data1.keys():
        print(k, "results=", dh.get(k))
        print(k, "ground truth=",dh.verify(k))
        print("----------------------------------")


    start = time.time()
    i = 0
    with open('names.csv', newline='', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        for row in reader:
            try:
                author = row[0]
                year = row[1]
                dh.put(author, year)
                i += 1
                if i >= 1000:
                    print(i)
                    break
            except:
                continue
    end = time.time()
    print("time=", end - start)
    '''
    while True:
        name = input("Enter a key: ")
        results = dh.get(name)
        #print(results)
        ground_truth = dh.verify(name)
        tp = 0
        fp = 0
        if len(ground_truth)>0:
          for r in results:
             key = list(r.keys())[0]
             if any(key in d for d in ground_truth):
                 tp+=1
             else:
                 fp +=1
          print("recall=", tp/len(ground_truth),"precision=", tp/(tp + fp))
    '''
    rs = 0
    ps = 0
    i = 0
    for k in dh.vs.keys():
        results = dh.get(k)
        # print(results)
        ground_truth = dh.verify(k)
        tp = 0
        fp = 0
        if len(ground_truth) > 0:
            i += 1
            for r in results:
                key = list(r.keys())[0]
                if key in ground_truth:
                    tp += 1
                else:
                    fp += 1
            rs += tp / len(ground_truth)
            ps += tp / (tp + fp)
            # if tp/len(ground_truth) < 0.9:
            #    print(results)
            #    print(ground_truth)
            #    print("recall",k, tp/len(ground_truth))
            #    print("precision", k, tp / (tp + fp))
    print("AVG RECALL", rs / i)
    print("AVG PRECISION", ps / i)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
