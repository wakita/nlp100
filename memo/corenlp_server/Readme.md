---
title: 'Stanford CoreNLP サーバの利用'
date: '2019-11-22'
---

@Ueda K くんのお手伝いで pywrap という名前の CoreNLP 用の Python API を試してみました。CoreNLP を使う人は使って下さい。ただし、注意があります。単に CoreNLP をインストールするだけでなく、その HTTP サーバ機能を動かさなくてはなりません。（設定は簡単）

CoreNLP は実行が遅くて処理をするのに一分くらいかかるような印象でしたが、その処理の大部分は Java VM の起動と膨大な NLP モデルの読み込みによるものです。サーバ版を利用すれば、一度、起動してモデルを読み込めば、それ以後の接続にはクイクイと答えてくれます。ですので、頻繁にリクエストを発行する場合はサーバを利用して下さい。かなりストレスが軽減されます。

一旦、CoreNLP サーバが稼動したら `pywrap` の実行はあまり難しくありません。ぼくの[リポジトリ](https://github.com/wakita/nlp100/tree/master/memo)を参考にして下さい。

- corenlp_server.sh: サーバを起動するスクリプト。.jar のあるディレクトリのありかを正確に参照すること。
- pywrap.py: サンプルコード

あと、CoreNLP サーバを起動したら、ブラウザで [http://localhost:9000](http://localhost:9000) を開くと面白いです。サンプル文書を与えると、以下のようなきれいな分析結果が見られます。
![](https://i.gyazo.com/7f64b317fbefe62bc93994b5365e2ef5.png)
