import database
import pickle
import tqdm
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stopwords = set(stopwords.words("english"))
vectorizer = database.Vectorize()
vctdb = database.VectorDB("databases/vectordb", vectorizer.dimension)
vctdb.open()
with open("databases/datadict.pkl", "rb") as f:
  dictdb = pickle.load(f) 
vectors = []
maxlen = 0
for key in tqdm.tqdm(dictdb.keys()):
  if isinstance(key, str):
    vectors.append(vectorizer(key).vector)
    maxlen = max(maxlen, len(set(key.split()) - stopwords))
    vctdb.insert(key, vectors[-1])

print("Max Length of Phrase: %d" % maxlen)
vctdb.write()
vectors = np.vstack(vectors)
clusterdb = database.VectorDB("databases/clusterdb", vectorizer.dimension)
clusterdb.open()
clusterdb = database.ClusterDB(clusterdb)
clusterdb.fit(vectors)
