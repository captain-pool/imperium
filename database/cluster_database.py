import numpy as np
import sklearn.cluster
# Disconnected Clusters don't have high dimensional holes only 0D disconnectedness



class ClusterDB:
  def __init__(self, vector_database):
    # Depends on max distance between similar points
    self.cst = sklearn.cluster.DBSCAN(eps=0.5)
    self.vct_db = vector_database
      
  def fit(self, vectors):
    assert not self.vct_db.initialized, "Vector DB is not empty."
    labels = self.cst.fit_predict(vectors)
    unique_labels = set(labels)
    centers = []
    for idx, ul in enumerate(unique_labels):
      idxs = np.where(labels == ul)
      vct_idxs = vectors[idxs]
      center = np.mean(vct_idxs, axis=0)
      self.vct_db.insert("center_%d" % idx, center)
    self.vct_db.write()

  def query(self, vector):
    assert self.vct_db.initialized, "Vector DB is not initialized"
    center = self.vct_db.nearest(vector, 1)[0] # Center Key
    center = self.vct_db.search_vector(center) # Center Vector
    dist = np.linalg.norm(center - vector)
    return dist
