#!/bin/sh

corenlp_dir="$HOME/Dropbox/Applications/stanford-corenlp-v392/"

(cd $corenlp_dir; java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000)
