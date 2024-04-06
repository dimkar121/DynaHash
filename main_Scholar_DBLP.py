import DynaHash as DH
import pandas as pd
from operator import itemgetter


if __name__ == '__main__':
  dh = DH.DynaHash()
  df1 = pd.read_csv("./data/DBLP2.csv", sep=",", encoding="utf-8", keep_default_na=False)
  df2 = pd.read_csv("./data/Scholar.csv", sep=",", encoding="utf-8", keep_default_na=False)
  truth = pd.read_csv("./data/truth_Scholar_DBLP.csv", sep=",", encoding="utf-8", keep_default_na=False)
  truthD = dict()
  a=0
  for i, r in truth.iterrows():
    idDBLP = r["idDBLP"]
    idScholar = r["idScholar"]
    if idDBLP in truthD:
        ids = truthD[idDBLP]
        ids.append(idScholar)
        a+=1
    else:
        truthD[idDBLP] = [idScholar]
  tt={}
  for k in truthD:
      if isinstance(truthD[k], list):
         tt[k] = len(truthD[k])
      else:
          tt[k] = 1
  res = dict(sorted(tt.items(), key=itemgetter(1), reverse=True)[:10])
  #print(res)
  matches = len(truthD.keys()) + a
  for i, r in df1.iterrows():
       id=r["id"]
       authors = r["authors"]
       title = r["title"]
       venue = r["venue"]
       year = str(r["year"])
       dh.add(title.lower()+" "+authors.lower(), id)
  tp = 0
  fp = 0
  #Scholars
  for i, r in df2.iterrows():
      authors = r["authors"]
      title = r["title"]
      venue = r["venue"]
      id = r["id"]
      year = str(r["year"])
      results, _, qtime= dh.get(title.lower()+" "+authors.lower())
      for r in results:
          idDBLP = r["v"]
          if idDBLP in truthD.keys():
            idScholars = truthD[idDBLP]
            for idScholar in idScholars:
                   if idScholar == id:
                      tp+=1
                   else:
                       fp+=1
          else:
              fp+=1
  print(tp, fp)
  print("recall=", round(tp/matches, 2), "precision=", round(fp/(tp+fp), 2))





