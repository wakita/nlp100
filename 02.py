#!/usr/bin/env python3

import io
import os
import sys
from pathlib import Path

from common import *

chapter('第2章: UNIXコマンドの基礎')
Path('2').mkdir(exist_ok=True)

# hightemp.txtは，日本の最高気温の記録を「都道府県」「地点」「℃」「日」のタブ区切り形式で格納したファイルである．以下の処理を行うプログラムを作成し，hightemp.txtを入力ファイルとして実行せよ．さらに，同様の処理をUNIXコマンドでも実行し，プログラムの実行結果を確認せよ．

datapath = 'data/hightemp.txt'
hightemp = datapath

# ファイルの読み込み。最後の改行を無視してsplitの邪魔にならないようにしている。
text = Path(hightemp).read_text()
text_lines = text[:-1].split('\n')


title('10. 行数のカウント')

# 行数をカウントせよ．確認にはwcコマンドを用いよ．

def wc(r, w):
    i = 0
    for _ in r: i = i + 1
    w.write(f'{i:8d} {datapath}\n')

with open(datapath) as r:
    with io.StringIO() as s:
        wc(r, s)
        my_answer = s.getvalue()
        assert s.getvalue() == system(f'wc -l {datapath}'), '10. 行数のカウント'


title('11. タブをスペースに置換')

# タブ1文字につきスペース1文字に置換せよ．確認にはsedコマンド，trコマンド，もしくはexpandコマンドを用いよ．

# gsed 's/\t/ /g' data/hightemp.txt # GNU sed
# cat data/hightemp.txt | tr '\t' ' '
# expand は使えないような気がするが。。。

def tr(s, r):
    for line in r:
        s.write(line.replace('\t', ' '))

unix_answer = system(f"tr '\t' ' ' < {hightemp}")
with open(datapath) as r:
    with io.StringIO() as s:
        tr(s, r)
        assert s.getvalue() == system(f"tr '\t' ' ' < {datapath}"), '11. タブをスペースに置換'


title('12. 1列目をcol1.txtに，2列目をcol2.txtに保存')

# 各行の1列目だけを抜き出したものをcol1.txtに，2列目だけを抜き出したものをcol2.txtとしてファイルに保存せよ．確認にはcutコマンドを用いよ．

lines = [line.split('\t') for line in text_lines]

def split(r, col1, col2):
    for line in r:
        line1, line2 = line.split('\t')[:2]
        col1.write(f'{line1}\n')
        col2.write(f'{line2}\n')

with open(datapath) as r, io.StringIO() as col1, io.StringIO() as col2:
    split(r, col1, col2)
    unix_answer = system('cut -f 1 data/hightemp.txt')
    assert col1.getvalue() == system('cut -f 1 data/hightemp.txt'), '12. 1列目をcol1.txtに'
    assert col1.getvalue() == system('cut -f 1 data/hightemp.txt'), '12. 2列目をcol2.txtに'


title('13. col1.txtとcol2.txtをマージ')

# 12で作ったcol1.txtとcol2.txtを結合し，元のファイルの1列目と2列目をタブ区切りで並べたテキストファイルを作成せよ．確認にはpasteコマンドを用いよ．

def merge(col1, col2, w):
    for l1, l2 in zip(col1, col2):
        w.write(f'{l1[:-1]}\t{l2[:-1]}\n')

with open(datapath) as r, open('2/12_col1.txt', 'wt') as col1, open('2/12_col2.txt', 'wt') as col2:
    split(r, col1, col2)
with open('2/12_col1.txt') as col1, open('2/12_col2.txt') as col2, io.StringIO() as col12:
    merge(col1, col2, col12)
    assert col12.getvalue() == system('paste 2/12_col1.txt 2/12_col2.txt'), 'Failure in (13. col1 + col2)'


title('14. 先頭からN行を出力')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のうち先頭のN行だけを表示せよ．確認にはheadコマンドを用いよ．

def head(n, r, w):
    i = 0
    for line in r:
        i = i + 1
        w.write(line)
        if i == n: break

with open('2/14.txt') as r, io.StringIO() as s:
    head(7, r, s)
    print(s.getvalue())
    assert s.getvalue() == system(f'head -n 7 {datapath}'), '14. 先頭からN行を出力'


title('15. 末尾のN行を出力')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のうち末尾のN行だけを表示せよ．確認にはtailコマンドを用いよ．

def tail(n, r, w):
    buf = [None] * n
    i = 0
    for line in r:
        buf[i % n] = line
        i = i + 1
    i = i % n
    for line in buf[i:] + buf[:i]:
        if line != None: w.write(line)

with open(datapath) as r, io.StringIO() as s:
    tail(7, r, s)
    assert s.getvalue() == system(f'tail -n 7 {datapath}'), '15. 末尾のN行を出力'


title('16. ファイルをN分割する')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のファイルを行単位でN分割せよ．同様の処理をsplitコマンドで実現せよ．

# remark: データ項目数がきれいに割り切れない場合に注意すること

abc = [chr(c) for c in range(ord('a'), ord('z')+1)]
ext = [c1+c2 for c1 in abc for c2 in abc]

def split(n, r, base):
    n_lines = len(lines)
    length = (n_lines + 1) // n
    starts = range(0, n_lines, length)
    texts = [lines[start :
                   start + length if start + length <= n_lines else n_lines]
             for start in starts]
    return ['\n'.join(text) + '\n' for text in texts]

from glob import glob

n_split = 5
parts = split(text_lines, n_split)
n_lines = len(text_lines)
system(f'split -l {(n_lines + 1) // n_split} {hightemp} 2/_16-')
files = sorted(glob('2/_16-*'))
assert len(parts) == len(files), '16. #split data'
for part, file in zip(parts, files):
    assert part == cat(file), f'16. {file}\n{part}'


title('17. １列目の文字列の異なり')

# 1列目の文字列の種類（異なる文字列の集合）を求めよ．確認にはsort, uniqコマンドを用いよ．

my_answer = set([line.split('\t')[0] for line in text_lines])
unix_answer = set(system(f'cut -f 1 {hightemp} | sort | uniq').split('\n')[:-1])
assert my_answer == unix_answer, '17. terms'

title('18. 各行を3コラム目の数値の降順にソート')

# 各行を3コラム目の数値の逆順で整列せよ（注意: 各行の内容は変更せずに並び替えよ）．確認にはsortコマンドを用いよ（この問題はコマンドで実行した時の結果と合わなくてもよい）．

print('my sort')
print('\n'.join(sorted(text_lines, key=lambda line: line.split('\t')[2])))

print('UNIX sort')
print(system(f'sort -k 3 {hightemp}'))

title('19. 各行の1コラム目の文字列の出現頻度を求め，出現頻度の高い順に並べる')

# 各行の1列目の文字列の出現頻度を求め，その高い順に並べて表示せよ．確認にはcut, uniq, sortコマンドを用いよ．'''

print('my term frequency')
cities = [line.split('\t')[0] for line in text_lines]
info = [(len(list(filter(lambda c: c == city, cities))), city)
        for city in set(cities)]
print('\n'.join(
    [f'{c:4d} {city}'
     for c, city in sorted(info, key=lambda i: i[0], reverse=True)]))

print('UNIX term frequency')
print(system(f'cut -f 1 {hightemp} | sort | uniq -c | sort -n -r'))
