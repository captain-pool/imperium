import database
import string
import nltk
import pickle
import collections
from nltk.corpus import stopwords
import nltk.stem
import absl.logging

Word = collections.namedtuple("Word", ["proper", "word", "vect"])

class SimSearch:
  MAX_PHRASE_LENGTH = 3
  def __init__(self, ddbpath, cdbpath, vctmodel):
    self._ddbpath = ddbpath
    self._cdbpath = cdbpath
    self.vct = vctmodel
    self.pstemmer = nltk.stem.PorterStemmer()
    vctdim = self.vct.dimension
    self.ddb = database.VectorDB(ddbpath, vctdim).open()
    with open("%s.pkl" % ddbpath, "rb") as f:
      self.dictdb = pickle.load(f) # Need to define
    cdb = database.VectorDB(cdbpath, vctdim).open()
    self.cdb = database.ClusterDB(cdb)
    nltk.download('stopwords')
    self.stopwds = set(stopwords.words("english"))

  def __reduce__(self):
    deserializer = SimSearch
    serialized_data = (self._ddbpath, self._cdbpath, self.vct)
    return deserializer, serialized_data

  def splitTokens(self, sentence):
    tokens = nltk.tokenize.word_tokenize(sentence)
    count = i = 0
    while i < len(tokens):
      currw = ""
      count = 0
      mindist = float("inf")
      minw = None
      prevvct = None
      prevw = None
      while count < SimSearch.MAX_PHRASE_LENGTH and i < len(tokens):
        currw = " ".join([currw, tokens[i]]).strip()
        if tokens[i] not in (self.stopwds | set(string.punctuation)):
          count += 1
        currwvct = self.vct(currw)
        if currwvct[-1].pos_ in database.Vectorize.NOUNS: # TODO: Fix Bug
          if prevw is not None:
            yield Word(word=prevw, proper=False, vect=prevvct.vector)
          currwvct = self.vct(tokens[i])
          minw = Word(word=tokens[i], proper=True, vect=currwvct.vector)
          i += 1
          break
        prevvct = currwvct
        prevw = currw
        dist = self.cdb.query(currwvct.vector)
        if dist < mindist:
          mindist = dist
          minw = Word(word=currw, proper=False, vect=currwvct.vector)
        i += 1
      yield minw

  def fingerspell(self, token):
    print("Token: %s" % token)

  def queryVideoClip(self, token):
    if token.proper:
      word = self.pstemmer.stem(token.word)
      url = self.dictdb.get(word, None)
      if not url:
        url = self.fingerspell(list(token.word))
    else:
      simtoken = self.ddb.nearest(token.vect, 1)[0]
      url = self.dictdb[simtoken]
    return url

  def query(self, sentence):
    urls = []
    for token in self.splitTokens(sentence):
      url = self.queryVideoClip(token)
      if isinstance(url, list):
        urls.extend(url)
      else:
        urls.append(url)
    return urls
