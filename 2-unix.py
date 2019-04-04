#!/usr/bin/env python3

import os
from pathlib import Path

from common import *

chapter('第2章: UNIXコマンドの基礎')
Path('2').mkdir(exist_ok=True)

# hightemp.txtは，日本の最高気温の記録を「都道府県」「地点」「℃」「日」のタブ区切り形式で格納したファイルである．以下の処理を行うプログラムを作成し，hightemp.txtを入力ファイルとして実行せよ．さらに，同様の処理をUNIXコマンドでも実行し，プログラムの実行結果を確認せよ．

hightemp = 'data/hightemp.txt'

# ファイルの読み込み。最後の改行を無視してsplitの邪魔にならないようにしている。
text = Path(hightemp).read_text()
text_lines = text[:-1].split('\n')


title('10. 行数のカウント')

# 行数をカウントせよ．確認にはwcコマンドを用いよ．

os.system(f'wc -l {hightemp}')
print(len(text_lines))


title('11. タブをスペースに置換')

# タブ1文字につきスペース1文字に置換せよ．確認にはsedコマンド，trコマンド，もしくはexpandコマンドを用いよ．

# gsed 's/\t/ /g' data/hightemp.txt # GNU sed
# cat data/hightemp.txt | tr '\t' ' '
# expand は使えないような気がするが。。。

unix_answer = system(f"tr '\t' ' ' < {hightemp}")
assert text.replace('\t', ' ') == unix_answer, 'Failure in (12. TAB -> SPACE)'


title('12. 1列目をcol1.txtに，2列目をcol2.txtに保存')

# 各行の1列目だけを抜き出したものをcol1.txtに，2列目だけを抜き出したものをcol2.txtとしてファイルに保存せよ．確認にはcutコマンドを用いよ．

lines = [line.split('\t') for line in text_lines]

with open('2/12_col1.txt', 'wt') as col1:
    col1.write('\n'.join([x for x, *_ in lines]) + '\n')
with open('2/12_col2.txt', 'wt') as col2:
    col2.write('\n'.join([x for _, x, *_ in lines]) + '\n')

unix_answer = system('cut -f 1 data/hightemp.txt')
assert cat('2/12_col1.txt') == unix_answer, 'Failure in (12. col1)'

unix_answer = system('cut -f 2 data/hightemp.txt')
assert cat('2/12_col2.txt') == unix_answer, 'Failure in (12. col2)'


title('13. col1.txtとcol2.txtをマージ')

# 12で作ったcol1.txtとcol2.txtを結合し，元のファイルの1列目と2列目をタブ区切りで並べたテキストファイルを作成せよ．確認にはpasteコマンドを用いよ．

col1 = Path('2/12_col1.txt').read_text().split('\n')[:-1]
col2 = Path('2/12_col2.txt').read_text().split('\n')[:-1]
Path('2/13_col12.txt').write_text('\n'.join([f'{x1}\t{x2}' for x1, x2 in zip(col1, col2)]) + '\n')

unix_answer = system('paste 2/12_col1.txt 2/12_col2.txt')
assert cat('2/13_col12.txt') == unix_answer, 'Failure in (13. col1 + col2)'


title('14. 先頭からN行を出力')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のうち先頭のN行だけを表示せよ．確認にはheadコマンドを用いよ．

def head(n, filepath):
    return '\n'.join(Path(filepath).read_text().split('\n')[:n]) + '\n'

Path('2/14.txt').write_text(head(7, hightemp))

assert cat('2/14.txt') == system(f'head -n 7 {hightemp}'), 'Failure in (14. head)'


title('15. 末尾のN行を出力')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のうち末尾のN行だけを表示せよ．確認にはtailコマンドを用いよ．

def tail(n, filepath):
    return '\n'.join(Path(filepath).read_text().split('\n')[-(n+1):-1]) + '\n'

Path('2/15.txt').write_text(tail(7, hightemp))
unix_answer = system(f'tail -n 7 {hightemp}')
assert cat('2/15.txt') == unix_answer, 'Failure in (15. tail)'

title('16. ファイルをN分割する')

# 自然数Nをコマンドライン引数などの手段で受け取り，入力のファイルを行単位でN分割せよ．同様の処理をsplitコマンドで実現せよ．

# remark: データ項目数がきれいに割り切れない場合に注意すること

def split(lines, n):
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
