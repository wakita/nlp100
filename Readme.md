# NLP100: Natural Language Processing dojo

- [Tutorial](http://www.cl.ecei.tohoku.ac.jp/nlp100/)

- [ken's issue](https://github.com/smartnova/19-allhands/issues/1)

# 入門方法

1. [NLP100プロジェクト](https://github.com/smartnova/19-allhands/projects/1)の `In progress`欄に自分用のカードを一枚追加し、以下のような内容を記入する。

    ```
    - [ ] 準備運動
    - [ ] UNIXコマンド
    - [ ] 正規表現
    - [ ] 形態素解析
    - [ ] 係り受け解析
    - [ ] 英語テキストの処理
    - [ ] データベース
    - [ ] 機械学習
    - [ ] ベクトル空間法 (I)
    - [ ] ベクトル空間法 (II)
    ```

1. カードを右クリックして *Convert to issue* を選択。自分用のIssueが作成されるので、そこに進捗状況を記録する。

1. 新しいGitHub repositoryを作成。脇田は`nlp100`と銘々した。

1. 作成したばかりの GitHub repository の URL をコピーし、Slack の `#nlp100` に以下のコマンドを記入する。

    `/github subscribe URL commits:all`

    これにより、実習作業をしてコミットするたびに Slack に通知を送れる。

# Stanford NLP の利用にあたって

6章で登場する[Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) は `brew install stanford-corenlp` でインストールできる Java アプリである。最新版の version 3.9.2 は Java 12 をサポートしているが、Homebrew に登録されている version 3.9.1 は Java 8 をターゲットとし、Java 9, Java 10 を非公式にサポートしているものの、Java 11 以降では利用できない。

すでに Java 8 はかなり古いシステムなので、以下では2019年3月に発表された Java 12 向けのインストール方法と実行方法を紹介する。

- Java 12 のインストール: `brew cask install java`

- [CoreNLPのDownloadページ](https://stanfordnlp.github.io/CoreNLP/download.html)から最新版のZipファイルをダウンロードする。2019-04-10現在、最新版はCoreNLP 3.9.2である。

- 便利のよい場所にZipファイルを展開する。脇田は `$HOME/Dropbox/Applications/stanford-corenlp-v392` として保存した。（ラップトップへのインストールは Dropbox に任せる）

- このままでは、コマンド実行が面倒なので、`$HOME/Dropbox/bin/corenlp` というスクリプトを用意し以下を記述した。

    ```
    #!/bin/sh
    
    $DROPBOX/Applications/stanford-corenlp-v392/corenlp.sh $*;
    ```

    `$HOME/Dropbox/bin` は `PATH` に含んでいるため、この設定を施せば `corenlp` コマンドがすぐに利用できるようになる。

- `corenlp` の実行: `corenlp -file data/nlp.txt -outputDirectory data` のようにやればよい。ファイルの出力先を指定しなくても構わない。
