import database
import string
import nltk
import collections
from nltk.corpus import stopwords

Word = collections.namedtuple("Word", ["proper", "word", "vect"])

class SimSearch:
  MAX_PHRASE_LENGTH = 5
  def __init__(self, ddbpath, cdbpath, vctmodelname):
    self.vct = database.Vectorizer(vctmodelname)
    vctdim = self.vct.dimension
    self.ddb = database.VectorDB(ddbpath, vctdim).open()
    self.dictdb = None # Need to define
    cdb = database.VectorDB(cdbpath, vctdim).open()
    self.cdb = database.ClusterDB(cdb)
    nltk.download('stopwords')
    self.stopwds = stopwords.words("english")

  def splitTokens(sentence):
    tokens = nltk.tokenize.word_tokenize(sentence)
    count = i = 0
    while i < length(tokens):
      currw = ""
      count = 0
      mindist = float("inf")
      minw = None
      while count < MAX_PHRASE_LENGTH and i < length(tokens):
        currw = " ".join([currw, tokens[i]]).strip()
        if tokens[i] not in (self.stopwds | set(string.punctuation)):
          count += 1
        currwvct = self.vct(currw)
        if currwvct.pos_ == self.vct.PROPER_NOUN:
          minw = Word(word=currw, proper=True, vect=self.vct.vector)
          break
        dist = self.cdb.query(currwvct)
        if dist < mindist:
          mindist = dist
          minw = Word(word=currw, proper=False, vect=self.vct.vector)
        i += 1
      yield minw

  def fingerspell(self, token):
    raise NotImplementedError

  def queryVideoClip(self, token):
    if token.proper:
      url = self.dictdb.get(token.word, None)
      if not url:
        url = self.fingerspell(list(token.word))
    else:
      simtoken = self.ddb.nearest(token.vect)
      url = self.dictdb[simtoken]
    return url

  def query(sentence):
    urls = []
    for token in self.splitTokens(sentence):
      url = self.queryVideoClip(token)
      if isinstance(url, list):
        urls.extend(url)
      else:
        urls.append(url)
    return urls
