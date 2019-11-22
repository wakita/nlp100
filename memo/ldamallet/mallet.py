from os.path import exists

from gensim import corpora
from gensim.models.wrappers import LdaMallet

'''
必要なもの

- brew install mallet
- conda install gensim

二回実行する。
1. 最初の実行は訓練。さまざまな学習データを生成する。
2. 二回目以後の実行はテスト。
学習モデルファイルの有無で二種類の実行を区別している。
'''

MALLET_PATH = '/usr/local/bin/mallet'

PREFIX     = 'docs-'
DICT_PATH  = 'docs.dict'
MODEL_PATH = 'docs.model'

raw_corpus = ["Human machine interface for lab abc computer applications",
              "A survey of user opinion of computer system response time",
              "The EPS user interface management system",
              "System and human system engineering testing of EPS",
              "Relation of user perceived response time to error measurement",
              "The generation of random binary unordered trees",
              "The intersection graph of paths in trees",
              "Graph minors IV Widths of trees and well quasi ordering",
              "Graph minors A survey"]
docs = [doc.split() for doc in raw_corpus]

if exists(MODEL_PATH):
    print('Testing...\n')
    dict = corpora.Dictionary.load(DICT_PATH)
    lda  = LdaMallet.load(MODEL_PATH)
    for doc in docs:
        topics = lda[dict.doc2bow(doc)]
        print(topics, doc)
else:
    print('Training...\n')
    dictionary = corpora.Dictionary(docs)
    dictionary.save(DICT_PATH)
    corpus = [dictionary.doc2bow(text) for text in docs]

    lda = LdaMallet(MALLET_PATH, corpus=corpus,
                    num_topics=3, workers=60, id2word=dictionary, iterations=50, prefix=PREFIX)
    lda.save(MODEL_PATH)
