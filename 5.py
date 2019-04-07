#!/usr/bin/env python3

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
        self.morphs = []

    def morph(self, line):
        self.morphs.append(Morph(line))

    def __str__(self):
        srcs = '' if self.srcs == [] else f'{str(self.srcs)[1:-1]} --> '
        dst = f' --> {self.dst}' if self.dst != -1 else ''
        morphs = ''.join([morph.surface for morph in self.morphs])
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

def text(chunk):
    return ''.join([m.surface
                    for m in chunk.morphs if m.pos != '記号'])

def srcdst(sentence):
    for chunk in sentence:
        if chunk.dst == -1: continue
        src, dst = text(chunk), text(sentence[chunk.dst])
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
        if ('名詞' in set([morph.pos for morph in chunk.morphs]) and
                '動詞' in set([morph.pos for morph in sentence[chunk.dst].morphs])):
            src = text(chunk)
            if src == '': continue
            dst = text(sentence[chunk.dst])
            yield src, dst

for src, dst in sv(sentences[3]):
    print(f'"{src}"\t"{dst}"')

with open('5/neko-sv.txt', 'wt') as w:
    for sentence in sentences:
        for src, dst in sv(sentence):
            w.write(f'"{src}"\t"{dst}"\n')


title('44. 係り受け木の可視化')

# 与えられた文の係り受け木を有向グラフとして可視化せよ．可視化には，係り受け木をDOT言語に変換し，Graphvizを用いるとよい．また，Pythonから有向グラフを直接的に可視化するには，pydotを使うとよい．


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
        if chunk.srcs == []: continue
        for morph in chunk.morphs:
            if morph.pos == '動詞': 動詞 = morph.base
            else: continue
            主部たち = [sentence[src].morphs for src in chunk.srcs]
            助詞たち = [主部[-1].surface for 主部 in 主部たち
                        if  len(主部) >= 2 and
                            主部[-1].pos == '助詞' and
                            主部[-2].pos == '名詞']
            if 助詞たち:
                w.write(f"{動詞}\t{' '.join(sorted(助詞たち))}\n")
            break

格パターン(sys.stdout, sentences[5])

with open('5/neko-格パターン.csv', 'wt') as w:
    for sentence in sentences:
        格パターン(w, sentence)

# Execute 45.sh


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
        if chunk.srcs == []: continue
        for morph in chunk.morphs:
            if morph.pos == '動詞': 動詞 = morph.base
            else: continue
            主部たち = [sentence[src].morphs for src in chunk.srcs]
            助詞_文節たち = [
                (主部[-1].surface, ''.join([m.surface for m in 主部]))
                for 主部 in 主部たち
                if  len(主部) >= 2 and
                    主部[-1].pos == '助詞' and
                    主部[-2].pos == '名詞']
            助詞_文節たち = sorted(助詞_文節たち, key=lambda 助詞_文節: 助詞_文節[0])
            if 助詞_文節たち:
                助詞たち, 文節たち = zip(*助詞_文節たち)
                w.write(f"{動詞}\t{' '.join(助詞たち)}\t{' '.join(文節たち)}\n")
            break

格フレーム情報(sys.stdout, sentences[5])

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
