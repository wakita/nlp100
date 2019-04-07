#!/usr/bin/env python3

import os.path
import json
import re

from common import *

chapter('第3章: 正規表現')

'''Wikipediaの記事を以下のフォーマットで書き出したファイルjawiki-country.json.gzがある．

1行に1記事の情報がJSON形式で格納される
各行には記事名が"title"キーに，記事本文が"text"キーの辞書オブジェクトに格納され，そのオブジェクトがJSON形式で書き出される
ファイル全体はgzipで圧縮される
以下の処理を行うプログラムを作成せよ．'''

if not os.path.exists('data/jawiki-country.json'):
    system('curl http://www.cl.ecei.tohoku.ac.jp/nlp100/data/jawiki-country.json.gz | gunzip - > data/jawiki-country.json')

title('20. JSONデータの読み込み')

# Wikipedia記事のJSONファイルを読み込み，「イギリス」に関する記事本文を表示せよ．問題21-29では，ここで抽出した記事本文に対して実行せよ．

with open('data/jawiki-country.json') as r:
    for line in r.readlines():
        article = json.loads(line)
        if article['title'] == 'イギリス':
            uk_text = article['text']
            break

with open('data/jawiki-uk.txt', 'wt') as w:
    w.write(uk_text)

uk_lines = uk_text.split('\n')

title('21. カテゴリ名を含む行を抽出')

# 記事中でカテゴリ名を宣言している行を抽出せよ．

re_category = re.compile('^\\[\\[Category:') # ]]
for line in uk_lines:
    if re_category.match(line):
        print(line)


title('22. カテゴリ名の抽出')

# 記事のカテゴリ名を（行単位ではなく名前で）抽出せよ．

re_category = re.compile('^\\[\\[Category:(.*)\\]\\]')
for line in uk_lines:
    m = re_category.match(line)
    if m: print(m[1])


title('23. セクション構造')

# 記事中に含まれるセクション名とそのレベル（例えば"== セクション名 =="なら1）を表示せよ．

# 参考 (MediaWiki の文法): https://www.mediawiki.org/wiki/Help:Formatting/ja

re_section = re.compile('^(=+)([^=].*[^=])=+')
for line in uk_lines:
    m = re_section.match(line)
    if m: print(len(m[1]) - 1, m[2])

title('24. ファイル参照の抽出')

# 記事から参照されているメディアファイルをすべて抜き出せ．

# [[File:Uk topo en.jpg|thumb|200px|イギリスの地形図]]
# ファイル:PalaceOfWestminsterAtNight.jpg|[[ウェストミンスター宮殿]]

## Solution 1
re_media_link = re.compile('^\[\[File:([^|]+)\|.*') # ]]
re_media_file = re.compile('^ファイル:([^|]+)\|.*')
for line in uk_lines:
    m = re_media_link.match(line)
    if m: print(f'media link: {m[1]}')
    m = re_media_file.match(line)
    if m: print(f'media file: {m[1]}')

## Solution 2
re_media = re.compile('(^\[\[File|^ファイル):([^|]+)\|.*') # ]]
for line in uk_lines:
    m = re_media.match(line)
    if m:
        kind = 'file' if m[1] == 'ファイル' else 'link'
        print(f'media({kind}): {m[2]}')

title('25. テンプレートの抽出')

# 記事中に含まれる「基礎情報」テンプレートのフィールド名と値を抽出し，辞書オブジェクトとして格納せよ．

'''
{{基礎情報 国
|略名 = イギリス
|日本語国名 = グレートブリテン及び北アイルランド連合王国
|公式国名 = {{lang|en|United Kingdom of Great Britain and Northern Ireland}}<ref>英語以外での正式国名:<br/>
...
|国際電話番号 = 44
|注記 = <references />
}}
'''

## Solution 1

re_combined = re.compile('|'.join([
    '{{基礎情報', # }}
    '\|([^ ]+) = (.+)',
    '}}\n']))

in_def = False
basic_info = dict()
for m in re_combined.finditer(uk_text):
    if not in_def and m[0].startswith('{{基礎情報'): # }}
        in_def = True; continue
    if in_def and m[0] == '}}\n': break
    if m[1]: basic_info[m[1]] = m[2]

# for k, v in basic_info.items(): print(f'{k} => {v}')

print(basic_info.keys())

## Solution 2

re_definition = re.compile('\|([^ ]+) = (.+)')
in_def = False
basic_info = dict()
for line in uk_lines:
    if line.startswith('{{基礎情報'): # }}
        in_def = True; continue
    if line.startswith('}}'):
        break
    m = re_definition.match(line)
    if m: basic_info[m[1]] = m[2]

print(basic_info.keys())


title('26. 強調マークアップの除去')

# 25の処理時に，テンプレートの値からMediaWikiの強調マークアップ（弱い強調，強調，強い強調のすべて）を除去してテキストに変換せよ（参考: マークアップ早見表）．

# 斜体テキスト	''斜体''
# 
# 太字テキスト	'''太字'''
# 
# 太字と斜体	'''''太字 & 斜体'''''

quotations = "'',''','''''".split(',')
rx = re.compile('|'.join([ f"{q}([^']+){q}" for q in quotations ]))
def strip_emph(text):
    return rx.sub(lambda m: m[1], text)

for k, v in basic_info.items():
    basic_info[k] = strip_emph(v)
    print(f'{k} => {v}')

title('27. 内部リンクの除去')

# 26の処理に加えて，テンプレートの値からMediaWikiの内部リンクマークアップを除去し，テキストに変換せよ（参考: マークアップ早見表）．

'''
https://www.mediawiki.org/wiki/Help:Links#Internal_links

Internal Links: 
[[Main Page]]
[[Help:Contents]]
[[Extension:DynamicPageList (Wikimedia)]]
'''

re_ilink = re.compile('\[\[([^]:]+)(:[^]]+)?\]\]')
def strip_ilink(text):
    return re_ilink.sub(lambda m: m[1], text)

for k, v in basic_info.items():
    basic_info[k] = strip_ilink(v)
    print(f'{k} => {basic_info[k]}')


title('28. MediaWikiマークアップの除去')

# 27の処理に加えて，テンプレートの値からMediaWikiマークアップを可能な限り除去し，国の基本情報を整形せよ．

'''
{{lang|en|United Kingdom of Great Britain and Northern Ireland}}
<ref>英語以外での正式国名:
<ref name="imf-statistics-gdp" />
<ref>[http://esa.un.org/.../population.htm United ... Affairs>Division> ... >Population]</ref>
<references />
<br/>
'''

rx = re.compile('|'.join(['{{[^}]+}}',
                          '<ref[^>]*>[^<]+</ref>',
                          '<ref [^>]+/>',
                          '<ref>[^:]+:',
                          '<references />',
                          '<br */>']))
def strip(text):
    return rx.sub('', text)

for k, v in basic_info.items():
    basic_info[k] = strip(v)
    print(f'{k} => {basic_info[k]}')


title('29. 国旗画像のURLを取得する')

# テンプレートの内容を利用し，国旗画像のURLを取得せよ．（ヒント: MediaWiki APIのimageinfoを呼び出して，ファイル参照をURLに変換すればよい）

import urllib.parse
import urllib.request
import requests

flag_image_name = basic_info['国旗画像']

# Solution 1
request_url = f'https://www.mediawiki.org/w/api.php?action=query&format=json&titles=File:{urllib.parse.quote(flag_image_name)}&prop=imageinfo&iiprop=url'
r = requests.get(request_url)
answer = r.json()
url = answer['query']['pages']['-1']['imageinfo'][0]['url']
system(f'open {url}')

# Solution 2 (Recommended)
mediawiki_api_url = 'https://www.mediawiki.org/w/api.php'
query_params = {
    'action': 'query',
    'format': 'json',
    'titles':  f'File:{flag_image_name}',
    'prop':   'imageinfo',
    'iiprop': 'url'
}

r = requests.get(mediawiki_api_url, params=query_params)
print(r.url)
url = r.json()['query']['pages']['-1']['imageinfo'][0]['url']
print(url)
system(f'open {url}')
