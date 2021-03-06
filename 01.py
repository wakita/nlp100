#!/usr/bin/env python3

from common import *

chapter('第1章: 準備運動')

title('00. 文字列の逆順')

# 文字列"stressed"の文字を逆に（末尾から先頭に向かって）並べた文字列を得よ．

print(''.join(reversed('stressed')))
print('stressed'[::-1])


title('01. 「パタトクカシーー」')

#「パタトクカシーー」という文字列の1,3,5,7文字目を取り出して連結した文字列を得よ．

print(''.join('パタトクカシーー'[1::2]))

title('02. 「パトカー」＋「タクシー」＝「パタトクカシーー」')

# 「パトカー」＋「タクシー」の文字を先頭から交互に連結して文字列「パタトクカシーー」を得よ．

pairs = [list(p) for p in zip('パトカー', 'タクシー')]

print(''.join(sum(pairs, [])))

from itertools import chain
print(''.join(chain.from_iterable(pairs)))

title('03. 円周率')

# "Now I need a drink, alcoholic of course, after the heavy lectures involving quantum mechanics."という文を単語に分解し，各単語の（アルファベットの）文字数を先頭から出現順に並べたリストを作成せよ．

words="Now I need a drink, alcoholic of course, after the heavy lectures involving quantum mechanics.".replace(',', '').replace('.', '').split()

print(*[len(w) for w in words])

title('04. 元素記号')

# "Hi He Lied Because Boron Could Not Oxidize Fluorine. New Nations Might Also Sign Peace Security Clause. Arthur King Can."という文を単語に分解し，1, 5, 6, 7, 8, 9, 15, 16, 19番目の単語は先頭の1文字，それ以外の単語は先頭に2文字を取り出し，取り出した文字列から単語の位置（先頭から何番目の単語か）への連想配列（辞書型もしくはマップ型）を作成せよ．

words = "Hi He Lied Because Boron Could Not Oxidize Fluorine. New Nations Might Also Sign Peace Security Clause. Arthur King Can.".replace('.', '').split()
indices1 = set([1, 5, 6, 7, 8, 9, 15, 16, 19])
indices2 = set([i+1 for i in range(len(words))]).difference(indices1)
atoms1 = dict([(words[i-1][:1], i) for i in indices1])
atoms2 = dict([(words[i-1][:2], i) for i in indices2])
print(dict(atoms1, **atoms2))

title('05. n-gram')

# 与えられたシーケンス（文字列やリストなど）からn-gramを作る関数を作成せよ．この関数を用い，"I am an NLPer"という文から単語bi-gram，文字bi-gramを得よ．

def n_gram(n, elems):
    return [elems[i:i+n] for i in range(len(elems) - n + 1)]

def n_wgram(n, words):
    return [tuple(words) for words in n_gram(n, words)]

def n_cgram(n, word):
    return [''.join(c) for c in n_gram(n, [c for c in word])]

sentence = "I am an NLPer"

print(n_wgram(2, sentence.split()))
print([n_cgram(2, w) for w in sentence.split()])


title('06. 集合')

# "paraparaparadise"と"paragraph"に含まれる文字bi-gramの集合を，それぞれ, XとYとして求め，XとYの和集合，積集合，差集合を求めよ．さらに，'se'というbi-gramがXおよびYに含まれるかどうかを調べよ．

def bi_cgram(word):
    return set(n_cgram(2, [c for c in word]))

s1, s2 = bi_cgram("paraparaparadise"), bi_cgram("paragraph")
for ans in [s1.union(s2), s1.intersection(s2), s1.difference(s2), 'se' in s1, 'se' in s2]:
    print(ans)

title('07. テンプレートによる文生成')

# 引数x, y, zを受け取り「x時のyはz」という文字列を返す関数を実装せよ．さらに，x=12, y="気温", z=22.4として，実行結果を確認せよ．

def fmt1(x, y, z):
    return '{}時の{}は{}'.format(x, y, z)

def fmt2(x, y, z):
    return '{0}時の{1}は{2}'.format(x, y, z)

def fmt3(x, y, z):
    return f'{x}時の{y}は{z}'

print(fmt1(12, '気温', 22.4))
print(fmt2(12, '気温', 22.4))
print(fmt3(12, '気温', 22.4))

title('08. 暗号文')

'''与えられた文字列の各文字を，以下の仕様で変換する関数cipherを実装せよ．

- 英小文字ならば(219 - 文字コード)の文字に置換
- その他の文字はそのまま出力
- この関数を用い，英語のメッセージを暗号化・復号化せよ．'''

def cipher(plain):
    return ''.join([chr(219 - ord(c)) if c.islower() else c for c in plain])

decipher = cipher

print(cipher('This is a secret message.'))
print(decipher(cipher('This is a secret message.')))

title('09. Typoglycemia')

'''スペースで区切られた単語列に対して，各単語の先頭と末尾の文字は残し，それ以外の文字の順序をランダムに並び替えるプログラムを作成せよ．ただし，長さが４以下の単語は並び替えないこととする．適当な英語の文（例えば"I couldn't believe that I could actually understand what I was reading : the phenomenal power of the human mind ."）を与え，その実行結果を確認せよ．'''

import random

def shuffle(w):
    if len(w) <= 4: return w
    L, M, R = [w[0]], [c for c in w[1:-1]], [w[-1]]
    return ''.join(L + random.sample(M, len(M)) + R)

text = "I couldn't believe that I could actually understand what I was reading : the phenomenal power of the human mind ."
print(' '.join([shuffle(w) for w in text.split()]))
