#!/usr/bin/env python3

import io
import itertools
import sys

from common import *

chapter('第5章: 係り受け解析')

# 夏目漱石の小説『吾輩は猫である』の文章（neko.txt）をCaboChaを使って係り受け解析し，その結果をneko.txt.cabochaというファイルに保存せよ．このファイルを用いて，以下の問に対応するプログラムを実装せよ．

system('''
if [ ! -x /usr/local/bin/cabocha ]; then brew install cabocha; fi
mkdir -p data 5
if [ ! -f data/neko.txt ]; then curl -o data/neko.txt http://www.cl.ecei.tohoku.ac.jp/nlp100/data/neko.txt; fi
if [ ! -f data/neko.txt.cabocha ]; then
       cabocha -f1 --output data/neko.txt.cabocha data/neko.txt
fi
''')

title('40. 係り受け解析結果の読み込み（形態素）')

# 形態素を表すクラスMorphを実装せよ．このクラスは表層形（surface），基本形（base），品詞（pos），品詞細分類1（pos1）をメンバ変数に持つこととする．さらに，CaboChaの解析結果（neko.txt.cabocha）を読み込み，各文をMorphオブジェクトのリストとして表現し，3文目の形態素列を表示せよ．

'''
EOS
* 0 1D 1/2 1.058678
　	記号,空白,*,*,*,*,　,　,　
どこ	名詞,代名詞,一般,*,*,*,どこ,ドコ,ドコ
で	助詞,格助詞,一般,*,*,*,で,デ,デ
* 1 4D 0/2 -1.453749
生れ	動詞,自立,*,*,一段,連用形,生れる,ウマレ,ウマレ
た	助動詞,*,*,*,特殊・タ,基本形,た,タ,タ
か	助詞,副助詞／並立助詞／終助詞,*,*,*,*,か,カ,カ
* 2 4D 0/0 -1.453749
とんと	副詞,一般,*,*,*,*,とんと,トント,トント
* 3 4D 0/1 -1.453749
見当	名詞,サ変接続,*,*,*,*,見当,ケントウ,ケントー
が	助詞,格助詞,一般,*,*,*,が,ガ,ガ
* 4 -1D 0/1 0.000000
つか	動詞,自立,*,*,五段・カ行イ音便,未然形,つく,ツカ,ツカ
ぬ	助動詞,*,*,*,特殊・ヌ,基本形,ぬ,ヌ,ヌ
。	記号,句点,*,*,*,*,。,。,。
'''

# neko: [[Morph]]

class Morph:
    def __init__(self, line):
        assert not line.startswith('*')
        assert not line.startswith('EOS')
        self.surface, attributes = line.split('\t')
        attributes = attributes.split(',')
        self.pos, self.pos1 = attributes[:2]
        self.base = attributes[6]

    def __str__(self):
        return f'Morph({self.surface})[{self.base}, {self.pos}, {self.pos1}]'

sentences = []
sentence = []

with open('data/neko.txt.cabocha') as r:
    for line in r:
        if line.startswith('EOS'):
            if sentence != []: sentences.append(sentence)
            sentence = []
        elif line.startswith('*'): pass
        else:
            sentence.append(Morph(line))

for m in sentences[3]: print(m)


title('41. 係り受け解析結果の読み込み（文節・係り受け）')

# 40に加えて，文節を表すクラスChunkを実装せよ．このクラスは形態素（Morphオブジェクト）のリスト（morphs），係り先文節インデックス番号（dst），係り元文節インデックス番号のリスト（srcs）をメンバ変数に持つこととする．さらに，入力テキストのCaboChaの解析結果を読み込み，１文をChunkオブジェクトのリストとして表現し，8文目の文節の文字列と係り先を表示せよ．第5章の残りの問題では，ここで作ったプログラムを活用せよ．

sentences = []
sentence = []
chunk = None

# * 0 1D 1/2 1.058678
class Chunk:
    def __init__(self, line):
        self.dst = int(line.split(' ')[2][:-1])
        self.srcs = []
        self._morphs = []

    def morph(self, line):
        self._morphs.append(Morph(line))

    def morphs(self, 記号=False):
        if 記号: return self._morphs
        return [m for m in self._morphs if m.pos != '記号']

    def text(self, 記号=False):
        return ''.join([m.surface for m in self.morphs(記号=記号)])

    def __str__(self):
        srcs = '' if self.srcs == [] else f'{str(self.srcs)[1:-1]} --> '
        dst = f' --> {self.dst}' if self.dst != -1 else ''
        morphs = ''.join([morph.surface for morph in self.morphs()])
        return f"{srcs}{morphs}{dst}"

with open('data/neko.txt.cabocha') as r:
    for line in r:
        if line.startswith('EOS'):
            if chunk: sentence.append(chunk); chunk = None
            if sentence != []: sentences.append(sentence)
            sentence = []
        elif line.startswith('*'):
            if chunk != None: sentence.append(chunk)
            chunk = Chunk(line)
        else: chunk.morph(line)
    if chunk: sentence.append(chunk)
    if sentence != []: sentences.append(sentence)

for sentence in sentences:
    for i, chunk in zip(range(len(sentence)), sentence):
        if chunk.dst >= 0: sentence[chunk.dst].srcs.append(i)

i = 0
for chunks in sentences[8]:
    print(f'{i}: {chunks}')
    i = i + 1


title('42. 係り元と係り先の文節の表示')

# 係り元の文節と係り先の文節のテキストをタブ区切り形式ですべて抽出せよ．ただし，句読点などの記号は出力しないようにせよ．

def srcdst(sentence):
    for chunk in sentence:
        if chunk.dst == -1: continue
        src, dst = chunk.text(), sentence[chunk.dst].text()
        if src != '' and dst != '': yield src, dst

for src, dst in srcdst(sentences[8]):
    print(f'"{src}"\t"{dst}"')

with open('5/neko-srcdest.txt', 'wt') as w:
    for sentence in sentences:
        for src, dst in srcdst(sentence):
            w.write(f'"{src}"\t"{dst}"\n')


title('43. 名詞を含む文節が動詞を含む文節に係るものを抽出')

# 名詞を含む文節が，動詞を含む文節に係るとき，これらをタブ区切り形式で抽出せよ．ただし，句読点などの記号は出力しないようにせよ．

def sv(sentence):
    for chunk in sentence:
        if chunk.dst == -1: continue
        if ('名詞' in set([morph.pos for morph in chunk.morphs()]) and
                '動詞' in set([morph.pos for morph in sentence[chunk.dst].morphs()])):
            src = chunk.text()
            if src == '': continue
            dst = sentence[chunk.dst].text()
            yield src, dst

for src, dst in sv(sentences[3]):
    print(f'"{src}"\t"{dst}"')

with open('5/neko-sv.txt', 'wt') as w:
    for sentence in sentences:
        for src, dst in sv(sentence):
            w.write(f'"{src}"\t"{dst}"\n')


title('44. 係り受け木の可視化')

# 与えられた文の係り受け木を有向グラフとして可視化せよ．可視化には，係り受け木をDOT言語に変換し，Graphvizを用いるとよい．また，Pythonから有向グラフを直接的に可視化するには，pydotを使うとよい．

import networkx as nx
import pygraphviz

def visualize(文):
    G = nx.Graph()
    for 節 in 文: G.add_node(節, label=節.text())
    for 節 in 文[:-1]: G.add_edge(節, 文[節.dst])
    g = nx.nx_agraph.to_agraph(G)
    g.draw(f"5/{''.join([節.text() for 節 in 文])}.pdf",
           format='pdf', prog='dot')

visualize(sentences[5])

title('45. 動詞の格パターンの抽出')

'''
今回用いている文章をコーパスと見なし，日本語の述語が取りうる格を調査したい． 動詞を述語，動詞に係っている文節の助詞を格と考え，述語と格をタブ区切り形式で出力せよ． ただし，出力は以下の仕様を満たすようにせよ．

動詞を含む文節において，最左の動詞の基本形を述語とする
述語に係る助詞を格とする
述語に係る助詞（文節）が複数あるときは，すべての助詞をスペース区切りで辞書順に並べる
「吾輩はここで始めて人間というものを見た」という例文（neko.txt.cabochaの8文目）を考える． この文は「始める」と「見る」の２つの動詞を含み，「始める」に係る文節は「ここで」，「見る」に係る文節は「吾輩は」と「ものを」と解析された場合は，次のような出力になるはずである．

始める  で
見る    は を
このプログラムの出力をファイルに保存し，以下の事項をUNIXコマンドを用いて確認せよ．

コーパス中で頻出する述語と格パターンの組み合わせ
「する」「見る」「与える」という動詞の格パターン（コーパス中で出現頻度の高い順に並べよ）
'''

# { 名詞 助詞 } --> { ... [動詞] ... 動詞 ... }: 最左の動詞の基本形
# 動詞 \t 助詞1 助詞2 ...: 空白区切り、辞書順

def 格パターン(w, sentence):
    for chunk in sentence:
        # 動詞を探索
        動詞 = None
        for morph in chunk.morphs():
            if morph.pos == '動詞':
                動詞 = morph
                break
        if not 動詞: continue
        主部たち = [sentence[src].morphs() for src in chunk.srcs]
        助詞たち = [主部[-1].surface for 主部 in 主部たち
                    if  len(主部) >= 2 and
                        主部[-2].pos == '名詞' and 主部[-1].pos == '助詞']
        if 助詞たち:
            w.write(f"{動詞.base}\t{' '.join(sorted(助詞たち))}\n")

correct_answer = '''始める\tで
見る\tは を
'''

with io.StringIO() as s:
    格パターン(s, sentences[5])
    assert s.getvalue() == correct_answer, '45. 動詞の格パターンの抽出'

with open('5/neko-格パターン.csv', 'wt') as w:
    for sentence in sentences:
        格パターン(w, sentence)

print(system('./45.sh'))


title('46. 動詞の格フレーム情報の抽出')

'''
45のプログラムを改変し，述語と格パターンに続けて項（述語に係っている文節そのもの）をタブ区切り形式で出力せよ．45の仕様に加えて，以下の仕様を満たすようにせよ．

項は述語に係っている文節の単語列とする（末尾の助詞を取り除く必要はない）
述語に係る文節が複数あるときは，助詞と同一の基準・順序でスペース区切りで並べる
「吾輩はここで始めて人間というものを見た」という例文（neko.txt.cabochaの8文目）を考える． この文は「始める」と「見る」の２つの動詞を含み，「始める」に係る文節は「ここで」，「見る」に係る文節は「吾輩は」と「ものを」と解析された場合は，次のような出力になるはずである．

始める  で      ここで
見る    は を   吾輩は ものを
'''

def 格フレーム情報(w, sentence):
    for chunk in sentence:
        # 動詞を探索
        動詞 = None
        for morph in chunk.morphs():
            if morph.pos == '動詞':
                動詞 = morph.base
                break
        if not 動詞: continue

        項たち = [sentence[src].morphs() for src in chunk.srcs]
        助詞_文節たち = [
            (項[-1].surface, ''.join([m.surface for m in 項]))
            for 項 in 項たち
            if  len(項) >= 2 and
                項[-2].pos == '名詞' and 項[-1].pos == '助詞']
        助詞_文節たち = sorted(助詞_文節たち,
                               key=lambda 助詞_文節: 助詞_文節[0])

        if 助詞_文節たち:
            助詞たち, 文節たち = zip(*助詞_文節たち)
            w.write(f"{動詞}\t{' '.join(助詞たち)}\t{' '.join(文節たち)}\n")

correct_answer = '''始める\tで\tここで
見る\tは を\t吾輩は ものを
'''

with io.StringIO() as s:
    格フレーム情報(s, sentences[5])
    print(s.getvalue())
    assert s.getvalue() == correct_answer, '46. 動詞の格フレーム情報の抽出'

with open('5/neko-格フレーム情報.csv', 'wt') as w:
    for sentence in sentences:
        格フレーム情報(w, sentence)

title('47. 機能動詞構文のマイニング')

'''
動詞のヲ格にサ変接続名詞が入っている場合のみに着目したい．46のプログラムを以下の仕様を満たすように改変せよ．

「サ変接続名詞+を（助詞）」で構成される文節が動詞に係る場合のみを対象とする
述語は「サ変接続名詞+を+動詞の基本形」とし，文節中に複数の動詞があるときは，最左の動詞を用いる
述語に係る助詞（文節）が複数あるときは，すべての助詞をスペース区切りで辞書順に並べる
述語に係る文節が複数ある場合は，すべての項をスペース区切りで並べる（助詞の並び順と揃えよ）
例えば「別段くるにも及ばんさと、主人は手紙に返事をする。」という文から，以下の出力が得られるはずである．

返事をする      と に は        及ばんさと 手紙に 主人は
このプログラムの出力をファイルに保存し，以下の事項をUNIXコマンドを用いて確認せよ．

コーパス中で頻出する述語（サ変接続名詞+を+動詞）
コーパス中で頻出する述語と助詞パターン
'''

def 機能動詞(w, sentence):
    for chunk in sentence:
        if chunk.srcs == []: continue
        for morph in chunk.morphs():
            if morph.pos == '動詞': 動詞 = morph.base
            else: continue
            # この動詞に「サ変接続名詞+を（助詞）」で構成される文節が係るか？
            サ変動詞 = None
            for src in chunk.srcs:
                主部 = sentence[src].morphs()
                if (len(主部) >= 2 and
                    主部[-1].pos == '助詞' and
                    主部[-1].surface == 'を' and
                    主部[-2].pos == '名詞' and
                    主部[-2].pos1 == 'サ変接続'):
                    サ変動詞 = sentence[src].text() + 動詞
                    サ変id = src
            if not サ変動詞: continue
            主部たち = [sentence[src].morphs() for src in chunk.srcs if src != サ変id]
            助詞_文節たち = [
                (主部[-1].surface, ''.join(m.surface for m in 主部))
                for 主部 in 主部たち
                if len(主部) >= 1 and 主部[-1].pos == '助詞']
            if 助詞_文節たち:
                助詞_文節たち = sorted(助詞_文節たち, key=lambda 助詞_文節: 助詞_文節[0])
                助詞たち, 文節たち = zip(*助詞_文節たち)
                w.write(f"{サ変動詞}\t{' '.join(助詞たち)}\t{' '.join(文節たち)}\n")
            break

'''
注意点：
「　別段くるにも及ばんさと、主人は手紙に返事をする。」
「及ばんさと、」で、読点を無視して判定しないと
「及ばんさと -> 返事をする」を取りこぼす。
'''

with open('5/neko-機能動詞.csv', 'wt') as w:
    for sentence in sentences:
        機能動詞(w, sentence)

correct_answer = '返事をする\tと に は\t及ばんさと 手紙に 主人は\n'

print(system('grep "及ばんさと" "5/neko-機能動詞.csv"'))
assert system('grep "及ばんさと" "5/neko-機能動詞.csv"') == correct_answer, '47. 機能動詞構文のマイニング'

title('48. 名詞から根へのパスの抽出')

'''
文中のすべての名詞を含む文節に対し，その文節から構文木の根に至るパスを抽出せよ． ただし，構文木上のパスは以下の仕様を満たすものとする．

各文節は（表層形の）形態素列で表現する
パスの開始文節から終了文節に至るまで，各文節の表現を"->"で連結する
「吾輩はここで始めて人間というものを見た」という文（neko.txt.cabochaの8文目）から，次のような出力が得られるはずである．

吾輩は -> 見た
ここで -> 始めて -> 人間という -> ものを -> 見た
人間という -> ものを -> 見た
ものを -> 見た
'''

def パス表現(文節列):
    return f"{' -> '.join([文節.text() for 文節 in 文節列])}"

def 根へのパス(w, sentence):
    for chunk in sentence:
        # 名詞を含む文節か？
        if not [morph for morph in chunk.morphs() if morph.pos == '名詞']:
            continue
        文節列 = [chunk]
        while chunk.dst != -1:
            chunk = sentence[chunk.dst]
            文節列.append(chunk)
        w.write(パス表現(文節列) + '\n')

correct_answer = '''吾輩は -> 見た
ここで -> 始めて -> 人間という -> ものを -> 見た
人間という -> ものを -> 見た
ものを -> 見た
'''

with io.StringIO() as s:
    根へのパス(s, sentences[5])
    print(s.getvalue())
    assert s.getvalue() == correct_answer, '48. 名詞から根へのパスの抽出'

with open('5/neko-根へのパス.txt', 'wt') as w:
    for sentence in sentences:
        根へのパス(w, sentence)

title('49. 名詞間の係り受けパスの抽出')

'''
文中のすべての名詞句のペアを結ぶ最短係り受けパスを抽出せよ．ただし，名詞句ペアの文節番号がi
とj
（i<j
）のとき，係り受けパスは以下の仕様を満たすものとする．

問題48と同様に，パスは開始文節から終了文節に至るまでの各文節の表現（表層形の形態素列）を"->"で連結して表現する
文節i
とj
に含まれる名詞句はそれぞれ，XとYに置換する
また，係り受けパスの形状は，以下の2通りが考えられる．

文節i
から構文木の根に至る経路上に文節j
が存在する場合: 文節i
から文節j
のパスを表示
上記以外で，文節i
と文節j
から構文木の根に至る経路上で共通の文節k
で交わる場合: 文節i
から文節k
に至る直前のパスと文節j
から文節k
に至る直前までのパス，文節k
の内容を"|"で連結して表示
例えば，「吾輩はここで始めて人間というものを見た。」という文（neko.txt.cabochaの8文目）から，次のような出力が得られるはずである．

Xは | Yで -> 始めて -> 人間という -> ものを | 見た
Xは | Yという -> ものを | 見た
Xは | Yを | 見た
Xで -> 始めて -> Y
Xで -> 始めて -> 人間という -> Y
Xという -> Y
'''

'''
解の方針

1. 名詞句の集合を得る
2. 名詞句対の「集合」を得る（ただし、自分とは対をなさないことに注意）
3. X* = [X, X.dst, ..., 根], Y* を計算
4. Y in X*: [X, ..., Y] を48の要領で表示
5. X in Y*: [Y, ..., X] を48の要領で表示
6. ほかの場合: X* と Y* の共通先祖を探す。以下のようになるはずだからリストの後ろから最長一致で探せばよい
      X* = [X, ..., [共通], ..., 根]
      Y* = [Y, ..., [共通], ..., 根]

注意: 名詞の X, Y へ破壊的に置換するとまずいことになると思う
'''

def 係り受けパス(w, 文):
    名詞節群 = [文節 for 文節 in 文
                  if '名詞' in [形態素.pos for 形態素 in 文節.morphs()]]
    名詞節対群 = []
    名詞節群1 = 名詞節群[:-1]
    for i, 名詞節1 in zip(range(len(名詞節群1)), 名詞節群1):
        for 名詞節2 in 名詞節群[i+1:]:
            名詞節対群.append([名詞節1, 名詞節2])

    def パス(節):
        p = [節]
        while 節.dst != -1:
            節 = 文[節.dst]
            p.append(節)
        return p

    def 抽象パス表現(パス, 名詞節1, 名詞節2):
        パス表現 = []
        for 節 in パス:
            if 節 == 名詞節1:
                パス表現.append(''.join([m.surface if m.pos != '名詞' else 'X'
                                         for m in 節.morphs()]))
            elif 節 == 名詞節2:
                パス表現.append(''.join([m.surface if m.pos != '名詞' else 'Y'
                                         for m in 節.morphs()]))
            else: パス表現.append(節.text())

        return ' -> '.join(パス表現)

    for 名詞節1, 名詞節2 in 名詞節対群:
        パス1, パス2 = パス(名詞節1), パス(名詞節2)

        try:
            i = パス1.index(名詞節2)
            w.write(抽象パス表現(パス1[:i+1], 名詞節1, 名詞節2) + '\n')
            continue
        except: pass

        try:
            i = パス2.index(名詞節1)
            w.write(抽象パス表現(パス2[:i+1], 名詞節1, 名詞節2) + '\n')
            continue
        except: pass

        for 節 in パス1[::-1]:
            if 節 in パス2: Z = 節
            else: break
        i = パス1.index(Z)
        共通パス表現 = パス表現(パス1[i:])
        パス1 = パス1[:i]
        パス2 = パス2[:パス2.index(Z)]
        パス表現1 = 抽象パス表現(パス1, 名詞節1, None)
        パス表現2 = 抽象パス表現(パス2, None, 名詞節2)
        w.write(f'{パス表現1} | {パス表現2} | {共通パス表現}\n')

# 以下のテストは100本ノックの説明から若干変更した。
# 100本ノックの説明は矛盾しているように思う。
# 仕様では名詞句を X, Y に置き換えるように書かれているが、出力サンプルでは
# 名詞を置き換え、それに続く助詞は置き換えられていない。
# おそらく出力サンプルが間違っているものと思われる。
# 出力サンプルに似せようと努力した結果、上述の実装は以下のような奇妙な出力(XX)を
# 含む：「XXで | Y -> 獰悪な | 種族であったそうだ」

correct_answer = '''Xは | Yで -> 始めて -> 人間という -> ものを | 見た
Xは | Yという -> ものを | 見た
Xは | Yを | 見た
Xで -> 始めて -> Yという
Xで -> 始めて -> 人間という -> Yを
Xという -> Yを
'''

with io.StringIO() as s:
    係り受けパス(s, sentences[5])
    print(s.getvalue())
    assert s.getvalue() == correct_answer, '49. 名詞間の係り受けパスの抽出'

with open('5/neko-係り受けパス.txt', 'wt') as w:
    for sentence in sentences:
        係り受けパス(w, sentence)
