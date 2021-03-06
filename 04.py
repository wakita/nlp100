#!/usr/bin/env python3

import itertools
from pathlib import Path
import random
import re

from common import *


chapter('第4章: 形態素解析')

'''
夏目漱石の小説『吾輩は猫である』の文章（neko.txt）をMeCabを使って形態素解析し，その結果をneko.txt.mecabというファイルに保存せよ．このファイルを用いて，以下の問に対応するプログラムを実装せよ．

なお，問題37, 38, 39はmatplotlibもしくはGnuplotを用いるとよい．
'''

system('''
mkdir -p data
cd data
if [ ! -f neko.txt ]
then curl -o neko.txt http://www.cl.ecei.tohoku.ac.jp/nlp100/data/neko.txt
fi

if [ ! -x /usr/local/bin/mecab ]; then brew install mecab mecab-ipadic; fi

if [ ! -f neko.txt.mecab ]; then mecab neko.txt > neko.txt.mecab; fi
''')



title('30. 形態素解析結果の読み込み')

# 形態素解析結果（neko.txt.mecab）を読み込むプログラムを実装せよ．ただし，各形態素は表層形（surface），基本形（base），品詞（pos），品詞細分類1（pos1）をキーとするマッピング型に格納し，1文を形態素（マッピング型）のリストとして表現せよ．第4章の残りの問題では，ここで作ったプログラムを活用せよ．

'''
吾輩    名詞,代名詞,一般,*,*,*,吾輩,ワガハイ,ワガハイ
は      助詞,係助詞,*,*,*,*,は,ハ,ワ
猫      名詞,一般,*,*,*,*,猫,ネコ,ネコ
で      助動詞,*,*,*,特殊・ダ,連用形,だ,デ,デ
ある    助動詞,*,*,*,五段・ラ行アル,基本形,ある,アル,アル
。      記号,句点,*,*,*,*,。,。,。
'''

re_mecab = re.compile('([^\t]+)\t(.*)')
keys = '表層形,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音'.split(',')

def mecab_obj(mecab_line):
    m = re_mecab.match(mecab_line)
    if m: return dict(zip(keys, [m[1]] + m[2].split(',')))

def load_mecab():
    text = Path('data/neko.txt.mecab').read_text()
    for sentence in [line for line in text.split('EOS\n') if line != '']:
        yield [mecab_obj(w) for w in sentence.split('\n') if w != '']

mecab = list(load_mecab())
for x in mecab[1]: print(x)

title('31. 動詞')

# 動詞の表層形をすべて抽出せよ．

verbs = set([w['表層形']
             for sentence in mecab for w in sentence
             if w['品詞'] == '動詞'])

print(f'表層形の数 = {len(verbs)}')
print('{', ', '.join(random.sample(verbs, 10)) + ', ... }')


title('32. 動詞の原形')

# 動詞の原形をすべて抽出せよ．

verbs = set([w['原形']
             for sentence in mecab for w in sentence
             if w['品詞'] == '動詞'])

print(f'原形の数 = {len (verbs)}')
print('{', ', '.join(random.sample(verbs, 10)) + ', ... }')

title('33. サ変名詞')

# サ変接続の名詞をすべて抽出せよ．

サ変接続名詞 = set([w['表層形']
                          for sentence in mecab for w in sentence
                          if w['品詞'] == '名詞' and w['品詞細分類1'] == 'サ変接続'])

print(f'サ変接続名詞の数 = {len(verbs)}')
print('{', ', '.join(random.sample(サ変接続名詞, 10)) + ', ... }')

title('34. 「AのB」')

# 2つの名詞が「の」で連結されている名詞句を抽出せよ．

re_AのB = re.compile('N>N')

def AのB(sentence, l, phrase):
    def code(w):
        if w['品詞'] == '名詞': return 'N'
        if w['品詞'] == '助詞' and w['表層形'] == 'の': return '>'
        return ' '

    s = ''.join([code(w) for w in sentence])
    for m in re_AのB.finditer(s):
        if len(m[0]) > l:
            l, phrase = len(m[0]), sentence[m.start():m.end()]
            print('.'.join([w['表層形'] for w in phrase]))
    return l, phrase

l, phrase = 0, ''
for sentence in mecab:
    l, phrase = AのB(sentence, l, phrase)

title('35. 名詞の連接')

# 名詞の連接（連続して出現する名詞）を最長一致で抽出せよ．

re_名詞列 = re.compile('NN+')

def 最長名詞列(文, l, 名詞列):
    def code(w): return 'N' if w['品詞'] == '名詞' else ' '

    for m in re_名詞列.finditer(''.join(map(code, 文))):
        if len(m[0]) > l:
            l, 名詞列 = len(m[0]), 文[m.start():m.end()]
            print('.'.join([w['表層形'] for w in 名詞列]))
    return l, 名詞列

l, 名詞列 = 0, ''
for 文 in mecab:
    l, 名詞列 = 最長名詞列(文, l, 名詞列)

title('36. 単語の出現頻度')

# 文章中に出現する単語とその出現頻度を求め，出現頻度の高い順に並べよ．

tf = dict()
word, c = None, 0
for w in sorted([w['表層形'] for sentence in mecab for w in sentence]):
    if w != word:
        if word: tf[word] = c
        word, c = w, 1
    else: c = c + 1
tf[word] = c
tf = sorted(tf.items(), key=lambda tc: tc[1], reverse=True)
print(' '.join([t[0] for t in tf[:20]]))

title('37. 頻度上位10語')

# 出現頻度が高い10語とその出現頻度をグラフ（例えば棒グラフなど）で表示せよ．

import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt
import numpy as np

font = { 'family': 'IPAexGothic' }

頻出語彙10 = tf[:10]

words, counts = zip(*tf[:10])
print(words, counts)
counts = np.array(counts)
ids = np.arange(len(words))

plt.bar(ids, counts)
plt.xticks(ids, words, **font)
plt.show()

title('38. ヒストグラム')

# 単語の出現頻度のヒストグラム（横軸に出現頻度，縦軸に出現頻度をとる単語の種類数を棒グラフで表したもの）を描け．

max_count = 20
histogram = np.zeros((max_count+1,), dtype=int)
for _, c in tf:
    i = min(c, max_count)
    histogram[i] = histogram[i] + 1

print(histogram)

plt.bar(np.arange(histogram.shape[0]), histogram)
plt.show()

title('39. Zipfの法則')

# 単語の出現頻度順位を横軸，その出現頻度を縦軸として，両対数グラフをプロットせよ．

_, counts = zip(*tf)
freq = np.array(counts)
print(counts[:100])
print(counts[-100:])
plt.scatter(1 + np.arange(freq.shape[0]), freq)
plt.xscale('log')
plt.yscale('log')
plt.show()
