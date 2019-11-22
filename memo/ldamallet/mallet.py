from os.path import exists

from gensim import corpora
from gensim.models.wrappers import LdaMallet

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

'''
from os.path import exists

def mallet(texts):
    import gensim
    import gensim.corpora as corpora
    from gensim.models.wrappers import LdaMallet

    mallet_path = "/usr/local/bin/mallet" # malletがあるパス
    model_path = "texts.mallet" #モデルを保存するパス

    if exists(model_path):
        return LdaMallet.load(str(model_path))
    else:
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        ldamallet = LdaMallet(mallet_path, corpus=corpus, num_topics=50, id2word=dictionary, prefix='docs-')
        ldamallet.save(model_path)
        return ldamallet

TEXTS = [ 'A classifier is an algorithm that distinguishes between a fixed set of classes such as "spam" vs non-spam based on labeled training examples', 'MALLET includes implementations of several classification algorithms including Naive Bayes Maximum Entropy and Decision Trees', 'In addition MALLET provides tools for evaluating classifiers' ]
TEXTS = [ sentence.split(' ') for sentence in TEXTS ]

mallet(TEXTS)
'''
