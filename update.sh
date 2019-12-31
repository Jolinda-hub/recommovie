#!/bin/sh
wget https://datasets.imdbws.com/title.basics.tsv.gz -P imdb/data/
wget https://datasets.imdbws.com/title.ratings.tsv.gz -P imdb/data/

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
python3 crawl.py config/config.ini

python3 -c "if 1:
  from util.elastic import Elastic
  import sys

  elastic = Elastic()
  diff = elastic.insert_elastic()

  if diff > 0:
      print(diff)
      sys.exit(1)
"

rm imdb/data/title.basics.tsv.gz
rm imdb/data/title.ratings.tsv.gz