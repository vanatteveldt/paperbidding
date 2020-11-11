#THANK YOU https://stackoverflow.com/a/35092200

import gensim
import numpy as np
from scipy import spatial
from unidecode import unidecode

from stopwords import ENGLISH_STOP_WORDS

VECTORS = "data/GoogleNews-vectors-negative300-SLIM.bin"


class Similarity:
    def __init__(self, model_file=VECTORS):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(VECTORS, binary=True)
        self.index2word_set = set(self.model.wv.index2word)

    @property
    def num_features(self):
        return self.model.wv.vectors.shape[1]

    @property
    def num_words(self):
        return self.model.wv.vectors.shape[0]

    def avg_feature_vector(self, sentence):
        words = sentence.split()
        feature_vec = np.zeros((self.num_features, ), dtype='float32')
        n_words = 0
        for word in words:
            word = word.lower()
            if word in ENGLISH_STOP_WORDS:
                continue

            if word in self.index2word_set:
                n_words += 1
                feature_vec = np.add(feature_vec, self.model[word])
        if n_words > 0:
            feature_vec = np.divide(feature_vec, n_words)
        return feature_vec

    def similarity(self, a, b):
        av = self.avg_feature_vector(a)
        bv = self.avg_feature_vector(b)
        return 1 - spatial.distance.cosine(av, bv)


def clean(x):
    return unidecode(x.lower().strip())


def _name(fn, ln):
    fn = clean(fn.split(" ")[0])
    ln = clean(ln.split(" ")[-1])
    return ", ".join([ln, fn])