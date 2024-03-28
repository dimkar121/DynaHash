import DynaHash as DH
import pandas as pd



if __name__ == '__main__':
  dh = DH.DynaHash(th=0.5)
  df1 = pd.read_csv("./data/DBLP.csv", sep=",", encoding="unicode_escape", keep_default_na=False)
  df2 = pd.read_csv("./data/ACM.csv", sep=",", encoding="unicode_escape", keep_default_na=False)
  truth = pd.read_csv("./data/truth_ACM_DBLP.csv", sep=",", encoding="utf-8", keep_default_na=False)
  truthD = dict()
  for i, r in truth.iterrows():
    idDBLP = str(r["idDBLP"])
    idACM = str(r["idACM"])
    truthD[idDBLP] = idACM
  for i, r in df1.iterrows():
       id=str(r["id"])
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
      id = str(r["id"])
      year = str(r["year"])
      results, _, _ = dh.get(title.lower()+" "+authors.lower())
      for r in results:
          idDBLP = str(r["v"])
          if idDBLP in truthD.keys():
              idACM = truthD[idDBLP]
              if idACM == id:
                   tp+=1
              else:
                   fp+=1
          else:
              fp+=1
  print(tp, fp)
  print("recall=", round(tp/len(truthD.keys()), 2), "precision=", round(tp/(tp+fp), 2))




