# Mallet で鍛えたモデルファイルを別のコンピュータで開けない問題について

`LdaMallet` で訓練するときにさまざまな中間データが出力される。デフォルトでは `/tmp/...` のどこかに出力される。

`LdaMallet` の `save` で保存されたモデルファイルを使って、テストするとき、実は `/tmp/...` のファイル群も活用される。このため、他の機械で同じモデルを活用しようとしても `/tmp/...` のファイルがないためにエラーとなってしまう。

このような不便を避けるために、`LdaMallet` は `prefix=` オプションによって、上述のようなファイルを生成する場所の変更を許している。サンプルコードの `LdaMallet(..., prefix=PREFIX)` を見て下さい。

ご参考: [Inferring doc topics from loaded LdaMallet fails due to missing corpus .mallet file](https://github.com/RaRe-Technologies/gensim/issues/818)
