#!/bin/sh

verbs=`cut -f 1 "5/neko-格パターン.csv" | \
       sort | uniq -c | sort -n -r | \
       head -n 5 | \
       sed 's/^ *//' | cut -f 2 -d ' '`

for v in $verbs; do
  res=`grep "$v" "5/neko-格パターン.csv" | \
    cut -f 2 | tr ' ' '\n' | \
    sort | uniq -c | sort -n -r | \
    sed 's/^ *//' | cut -f 2 -d ' '`
  echo "【"$v"】"
  echo $res
done
