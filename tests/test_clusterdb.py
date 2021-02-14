import database
import numpy as np

a = np.random.normal(size=[10, 100]).astype(np.float32)
b = np.random.normal(size=[10, 100]).astype(np.float32) + 5.0
c = np.vstack([a, b])
db = database.VectorDatabase('tmpdb', 100)
db.open()
cdb = database.ClusterDB(db)
cdb.fit(c)
