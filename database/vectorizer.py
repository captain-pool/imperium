import numpy as np
import spacy
from absl import logging

class Vectorize(object):

  NOUNS = {"PROPN", "NOUN"}
  def __init__(self, model="en_core_web_sm"):
    logging.info(f"Loading {model} for vectorizing")
    if model.lower().strip() == "en_core_web_sm":
      logging.warn("Not the right model for vectorizing statements, loading anyway")
    self._model_name = model
    self._vmodel = spacy.load(self._model_name)
    self._vdim = self._vmodel("dummy").vector.shape[0]

  @property
  def dimension(self):
    return self._vdim
  def __call__(self, sentence):
    obj = self._vmodel(sentence)
    obj.vector = obj.vector[np.newaxis,:].astype(np.float32)
    return obj
