#!/usr/bin/env python3

from pathlib import Path
import re

from stemming.porter2 import stem

from common import *

chapter('第6章: 英語テキストの処理')

# 英語のテキスト（nlp.txt）に対して，以下の処理を実行せよ．

system('''
if [ ! -f data/nlp.txt ]; then
  curl -o data/nlp.txt http://www.cl.ecei.tohoku.ac.jp/nlp100/data/nlp.txt
fi

mkdir -p 6''')


title ('50. 文区切り')

# (. or ; or : or ? or !) → 空白文字 → 英大文字というパターンを文の区切りと見なし，入力された文書を1行1文の形式で出力せよ．

text = Path('data/nlp.txt').read_text()

re_statement_delimiter = re.compile(r'(?<=[.;:?!])\s+(?=[A-Z])')

text = re_statement_delimiter.split(text)
for line in text[:5]: print(line)


title ('51. 単語の切り出し')

# 空白を単語の区切りとみなし，50の出力を入力として受け取り，1行1単語の形式で出力せよ．ただし，文の終端では空行を出力せよ．

re_whitespaces = re.compile(r'\s+')

with open('6/words.txt', 'wt') as w:
    for line in text:
        if line != '': w.write('\n'.join(re_whitespaces.split(line)) + '\n\n')


title ('52. ステミング')

# 51の出力を入力として受け取り，Porterのステミングアルゴリズムを適用し，単語と語幹をタブ区切り形式で出力せよ． Pythonでは，Porterのステミングアルゴリズムの実装としてstemmingモジュールを利用するとよい．

re_word = re.compile(r'(\w+)')

with open('6/words.txt') as r, open('6/stems.txt', 'wt') as w:
    for line in r:
        m = re_word.match(line)
        if m:
            word = m.group(1)
            w.write(f'{word}\t{stem(word)}\n')
        else: w.write('\n')

title ('53. Tokenization')

# Stanford Core NLPを用い，入力テキストの解析結果をXML形式で得よ．また，このXMLファイルを読み込み，入力テキストを1行1単語の形式で出力せよ．

# Stanford CoreNLP のインストール方法については Readme.md を参照のこと。

system('''
if [ ! -f data/nlp.txt.xml ]; then
       corenlp -file data/nlp.txt -outputDirectory data
fi''')

import xml.sax
from xml.sax.handler import ContentHandler

class CoreNLP53(ContentHandler):
    def __init__(self, w):
        self.stack = []
        self.w = w
        
    def startElement(self, name, attrs):
        self.stack.append(name)

    def endElement(self, name):
        self.stack = self.stack[:-1]

    def characters(self, content):
        if self.stack[-1] == 'word':
            self.w.write(content + '\n')

def main53():
    with open('data/nlp.txt.xml') as r, open('data/nlp-words.txt', 'wt') as w:
        parser = xml.sax.make_parser()
        parser.setContentHandler(CoreNLP53(w))
        parser.parse(r)
    n_words = 10
    print(f'## First {n_words} words\n')
    print(system(f'head -n {n_words} data/nlp-words.txt'))

main53()

title ('54. 品詞タグ付け')

# Stanford Core NLPの解析結果XMLを読み込み，単語，レンマ，品詞をタブ区切り形式で出力せよ．

class CoreNLP54(ContentHandler):
    def __init__(self, w):
        self.stack = []
        self.info = None
        self.w = w
        
    def startElement(self, name, attrs):
        self.stack.append(name)
        if name == 'token': self.info = dict()

    def endElement(self, name):
        self.stack = self.stack[:-1]
        if name == 'token':
            info = self.info
            self.w.write(f"{info['word']}\t{info['lemma']}\t{info['POS']}\n")

    def characters(self, content):
        element = self.stack[-1]
        if element in ['word', 'lemma', 'POS']: self.info[element] = content

def main54():
    with open('data/nlp.txt.xml') as r, open('data/nlp-pos.tsv', 'wt') as w:
        parser = xml.sax.make_parser()
        parser.setContentHandler(CoreNLP54(w))
        parser.parse(r)

    n_words = 10
    print(f'## First {n_words} words\n')
    print(system(f'head -n {n_words} data/nlp-pos.tsv'))

main54()


title ('55. 固有表現抽出')

# 入力文中の人名をすべて抜き出せ．

class CoreNLP55(ContentHandler):
    def __init__(self, w):
        self.stack = []
        self.token = None
        self.person_name = []
        self.w = w
        
    def startElement(self, name, attrs):
        self.stack.append(name)
        if name == 'token': self.token = dict()

    def endElement(self, name):
        self.stack = self.stack[:-1]
        if name == 'token':
            if self.token['NER'] == 'PERSON':
                self.person_name.append(self.token['word'])
            else:
                if self.person_name: print(' '.join(self.person_name))
                self.person_name = []

    def characters(self, content):
        element = self.stack[-1]
        if element in ['word', 'NER']: self.token[element] = content

def main55():
    with open('data/nlp.txt.xml') as r:
        parser = xml.sax.make_parser()
        parser.setContentHandler(CoreNLP55(w))
        parser.parse(r)

main55()


title ('56. 共参照解析')

# Stanford Core NLPの共参照解析の結果に基づき，文中の参照表現（mention）を代表参照表現（representative mention）に置換せよ．ただし，置換するときは，「代表参照表現（参照表現）」のように，元の参照表現が分かるように配慮せよ．
'''
      <coreference>
        <mention representative="true">
          <sentence>37</sentence>
          <start>5</start>
          <end>8</end>
          <head>7</head>
          <text>machine learning algorithms</text>
        </mention>
        <mention>
          <sentence>38</sentence>
          <start>1</start>
          <end>3</end>
          <head>2</head>
          <text>These algorithms</text>
        </mention>
      </coreference>
'''

class

class P56Coref(ContentHandler):
    def __init__(self, w):
        self.stack = []
        self.token = None
        self.person_name = []
        self.w = w

    def startElement(self, name, attrs):
        self.stack.append(name)
        if name == 'mension':

            if 'representative' in attrs.keys():
                if 
                coref['representative'] = attrs
                if attrs['representative'] == 'true':
                    self.coref

    def endElement(self, name):
        self.stack = self.stack[:-1]
        if name == 'token':
            if self.token['NER'] == 'PERSON':
                self.person_name.append(self.token['word'])
            else:
                if self.person_name: print(' '.join(self.person_name))
                self.person_name = []

    def characters(self, content):
        element = self.stack[-1]
        if element in ['word', 'NER']: self.token[element] = content

    @staticmethod
    def run():
        with open('data/nlp.txt.xml') as r:
            parser = xml.sax.make_parser()
            parser.setContentHandler(CoreNLP56(w))
            parser.parse(r)

CoreNLP56.run()


title ('57. 係り受け解析')

# Stanford Core NLPの係り受け解析の結果（collapsed-dependencies）を有向グラフとして可視化せよ．可視化には，係り受け木をDOT言語に変換し，Graphvizを用いるとよい．また，Pythonから有向グラフを直接的に可視化するには，pydotを使うとよい．


title ('58. タプルの抽出')

'''
Stanford Core NLPの係り受け解析の結果（collapsed-dependencies）に基づき，「主語 述語 目的語」の組をタブ区切り形式で出力せよ．ただし，主語，述語，目的語の定義は以下を参考にせよ．

述語: nsubj関係とdobj関係の子（dependant）を持つ単語
主語: 述語からnsubj関係にある子（dependent）
目的語: 述語からdobj関係にある子（dependent）
'''


title ('59. S式の解析')

# Stanford Core NLPの句構造解析の結果（S式）を読み込み，文中のすべての名詞句（NP）を表示せよ．入れ子になっている名詞句もすべて表示すること．

