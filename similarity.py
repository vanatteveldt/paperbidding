#THANK YOU https://stackoverflow.com/a/35092200

import gensim
import numpy as np
from scipy import spatial
from stopwords import ENGLISH_STOP_WORDS

VECTORS = "GoogleNews-vectors-negative300.bin"
VECTORS = "data/GoogleNews-vectors-negative300-SLIM.bin"

class Similarity:

    def __init__(self, model_file=VECTORS):
        #print("Loading word2vec model from ", model_file)
        self.model = gensim.models.KeyedVectors.load_word2vec_format(VECTORS, binary=True)
        self.index2word_set = set(self.model.wv.index2word)
        self.num_features = 300  # why is this a parameter?


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
        if (n_words > 0):
            feature_vec = np.divide(feature_vec, n_words)
        return feature_vec

    def similarity(self, a, b):
        av = self.avg_feature_vector(a)
        bv = self.avg_feature_vector(b)
        return 1 - spatial.distance.cosine(av, bv)



