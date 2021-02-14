import database
import pickle
import tqdm
import numpy as np
import nltk
from nltk.corpus import stopwords
import nltk.stem
import copy

nltk.download('stopwords')
ps = nltk.stem.PorterStemmer()
stopwords = set(stopwords.words("english"))
vectorizer = database.Vectorize()
vctdb = database.VectorDB("databases/vectordb", vectorizer.dimension)
vctdb.open()
with open("databases/vectordb.pkl", "rb") as f:
  dictdb = pickle.load(f)
vectors = []
maxlen = 0
dictdbwstem = copy.deepcopy(dictdb)
for key in tqdm.tqdm(dictdb.keys()):
  if isinstance(key, str):
    vect = vectorizer(key)
    vectors.append(vect.vector)
    vctdb.insert(key, vectors[-1])
    stemkey = ps.stem(key)
    dictdbwstem[stemkey] = dictdb[key]
    maxlen = max(maxlen, len(set(key.split()) - stopwords))

with open("databases/vectordb.pkl", "wb") as f:
  pickle.dump(dictdbwstem, f)

print("Max Length of Phrase: %d" % maxlen)
vctdb.write()
vectors = np.vstack(vectors)
clusterdb = database.VectorDB("databases/clusterdb", vectorizer.dimension)
clusterdb.open()
clusterdb = database.ClusterDB(clusterdb)
clusterdb.fit(vectors)
