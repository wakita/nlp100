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

class CoreNLPHandler(ContentHandler):
    def __init__(self, w=None):
        self.stack = []
        self.w = w

    def startElement(self, name, attrs):
        node = { 'tag': name }
        self.stack.append(node)
        return node

    def endElement(self, name):
        element = self.stack[-1]
        self.stack = self.stack[:-1]
        return element

    def characters(self, content): return self.top()

    def top(self, tag=None):
        S = self.stack
        if tag:
            for i in reversed(range(len(S))):
                if S[i]['tag'] == tag: return S[i]
            return None
        else: return S[-1]


class P53Handler(CoreNLPHandler):
    def characters(self, content):
        if self.top('word'): self.w.write(content + '\n')

with open('data/nlp.txt.xml') as r, open('data/nlp-words.txt', 'wt') as w:
    parser = xml.sax.make_parser()
    parser.setContentHandler(P53Handler(w))
    parser.parse(r)

n_words = 10
print(f'## First {n_words} words\n')
print(system(f'head -n {n_words} data/nlp-words.txt'))

title ('54. 品詞タグ付け')

# Stanford Core NLPの解析結果XMLを読み込み，単語，レンマ，品詞をタブ区切り形式で出力せよ．

class P54Handler(CoreNLPHandler):
    def endElement(self, name):
        element = super().endElement(name)
        if element['tag'] == 'token':
            token = element
            self.w.write(f"{token['word']}\t{token['lemma']}\t{token['POS']}\n")

    def characters(self, content):
        attr = super().characters(content)['tag']
        if attr in ['word', 'lemma', 'POS']:
            self.top('token')[attr] = content

with open('data/nlp.txt.xml') as r, open('data/nlp-pos.tsv', 'wt') as w:
    parser = xml.sax.make_parser()
    parser.setContentHandler(P54Handler(w))
    parser.parse(r)

n_words = 10
print(f'## First {n_words} words\n')
print(system(f'head -n {n_words} data/nlp-pos.tsv'))


title ('55. 固有表現抽出')

# 入力文中の人名をすべて抜き出せ．

class P55Handler(CoreNLPHandler):
    person_name = []

    def endElement(self, name):
        element = super().endElement(name)
        if element['tag'] == 'token':
            token = element
            if token['NER'] == 'PERSON': self.person_name.append(token['word'])
            elif self.person_name:
                print(' '.join(self.person_name))
                self.person_name = []
        elif name == 'sentence' and self.person_name:  # 文末が人名な場合への対応
            print(' '.join(self.person_name))
            self.person_name = []

    def characters(self, content):
        attr, token = super().characters(content)['tag'], self.top('token')
        if attr in ['word', 'NER'] and token: token[attr] = content

with open('data/nlp.txt.xml') as r:
    parser = xml.sax.make_parser()
    parser.setContentHandler(P55Handler())
    parser.parse(r)


title ('56. 共参照解析')

# Stanford Core NLPの共参照解析の結果に基づき，文中の参照表現（mention）を代表参照表現（representative mention）に置換せよ．ただし，置換するときは，「代表参照表現（参照表現）」のように，元の参照表現が分かるように配慮せよ．

class FindCoref(CoreNLPHandler):
    substitutions = []

    def startElement(self, name, attrs):
        node = super().startElement(name, attrs)
        if name == 'mention':
            coreference = self.top('coreference')
            if attrs.get('representative'): coreference['mentions'] = []
            coreference['mentions'].append(node)

    def endElement(self, name):
        node = super().endElement(name)
        if name == 'coreference':
            mentions = node.get('mentions')
            if mentions:
                replacement = mentions[0]['text']  # representative mention
                for m in mentions[1:]:
                    self.substitutions.append((m, replacement))

    def characters(self, content):
        attr = self.top()['tag']
        mention = self.top('mention')
        if mention:
            if attr in ['sentence', 'start', 'end']: mention[attr] = int(content)
            elif attr == 'text': mention[attr] = content

with open('data/nlp.txt.xml') as r:
    parser = xml.sax.make_parser()
    finder = FindCoref()
    parser.setContentHandler(finder)
    parser.parse(r)

substitutions = sorted(finder.substitutions,
                       key=lambda subst: [subst[0]['sentence'], subst[0]['start'], subst[0]['end']])
# for subst in substitutions: print(subst)

class ApplyCoref(CoreNLPHandler):
    substitutions = []
    parsing_done = False

    def __init__(self, substitutions):
        super().__init__(self)
        self.substitutions = substitutions

    def startElement(self, name, attrs):
        if self.parsing_done: return
        node = super().startElement(name, attrs)
        if name == 'token':
            node['id'] = attrs['id']
        if name == 'sentence' and self.top('sentences'):
            node['id'] = attrs['id']
            node['pos'] = 0
            node['tokens'] = []

    def endElement(self, name):
        if self.parsing_done: return
        node = super().endElement(name)
        if name == 'token': self.top('sentence')['tokens'].append(node)
        if name == 'sentence':
            sentence = node
            (subst, replacement), *_ = S = self.substitutions
            sentence_id = int(sentence['id'])
            if subst['sentence'] != sentence_id: return

            pos, words = 0, []
            for token in sentence['tokens']:
                if words: words.append(' ' * (token['CharacterOffsetBegin'] - pos))
                words.append(token['word'])
                pos = token['CharacterOffsetEnd']
                if int(token['id']) == subst['end'] - 1:
                    words.append(f' ({replacement})')
                    coref = True
                    if len(S) > 1: (subst, replacement), *_ = S = S[1:]
            self.substitutions = S

            print(f'\n{"".join(words)}')
        if name == 'sentences': self.parsing_done = True

    def characters(self, content):
        if self.parsing_done: return
        super().characters(content)
        node = self.top()
        tag = node['tag']
        if tag in ['CharacterOffsetBegin', 'CharacterOffsetEnd']:
            self.top('token')[tag] = int(content)
        elif tag == 'word': self.top('token')[tag] = content

with open('data/nlp.txt.xml') as r:
    parser = xml.sax.make_parser()
    parser.setContentHandler(ApplyCoref(substitutions))
    parser.parse(r)


title ('57. 係り受け解析')

# Stanford Core NLPの係り受け解析の結果（collapsed-dependencies）を有向グラフとして可視化せよ．可視化には，係り受け木をDOT言語に変換し，Graphvizを用いるとよい．また，Pythonから有向グラフを直接的に可視化するには，pydotを使うとよい．

import networkx as nx
import pygraphviz

class P57Handler(CoreNLPHandler):
    G = nx.Graph()
    nodes = set()
    edges = set()
    collapsed_dependencies = False

    def startElement(self, name, attrs):
        node = super().startElement(name, attrs)
        if name == 'dependencies':
            self.collapsed_dependencies = (attrs['type'] == 'collapsed-dependencies')
        if name == 'dep': node['type'] = attrs['type']
        if name in ['governor', 'dependent']:
            self.top('dep')[name] = node
            node['idx'] = attrs['idx']

    def endElement(self, name):
        node = super().endElement(name)
        if name == 'dependencies': self.collapsed_dependencies = False
        if name == 'dep':
            governor, dependent = node['governor']['label'], node['dependent']['label']
            G = self.G
            if not governor in self.nodes:
                self.nodes.add(governor)
                G.add_node(governor)
            if not dependent in self.nodes:
                self.nodes.add(dependent)
                G.add_node(dependent)
            G.add_edge(governor, dependent, label=node['type'])

    def characters(self, content):
        node = super().characters(content)
        if node['tag'] in ['governor', 'dependent']:
            node['label'] = content

with open('data/bills.txt.xml') as r:
    parser = xml.sax.make_parser()
    handler = P57Handler()
    parser.setContentHandler(handler)
    parser.parse(r)
    G = handler.G
    g = nx.nx_agraph.to_agraph(G)
    g.draw('data/bills.txt.pdf', format='pdf', prog='dot')


title ('58. タプルの抽出')

'''
Stanford Core NLPの係り受け解析の結果（collapsed-dependencies）に基づき，「主語 述語 目的語」の組をタブ区切り形式で出力せよ．ただし，主語，述語，目的語の定義は以下を参考にせよ．

述語: nsubj関係とdobj関係の子（dependant）を持つ単語
主語: 述語からnsubj関係にある子（dependent）
目的語: 述語からdobj関係にある子（dependent）
'''


title ('59. S式の解析')

# Stanford Core NLPの句構造解析の結果（S式）を読み込み，文中のすべての名詞句（NP）を表示せよ．入れ子になっている名詞句もすべて表示すること．

