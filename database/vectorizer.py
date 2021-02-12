import spacy
from absl import logging

class Vectorize(object):
  def __init__(self, model="en_core_web_sm"):
    logging.info(f"Loading {model} for vectorizing")
    if model.lower().strip() == "en_core_web_sm":
      logging.warn("Not the right model for vectorizing statements, loading anyway")
    self._model_name = model
  def open(self):
    self._vmodel = spacy.load(self._model_name)
  def vectorize(self, sentence):
    return self._vmodel(sentence).vector
