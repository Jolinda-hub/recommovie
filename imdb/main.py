# -*- coding: utf-8 -*-
import concurrent.futures
from crawler import Crawler
from db_connection import DbConnection
from data import *


def main():
    crawler = Crawler()
    db = DbConnection()

    # df = get_data(offline=True)
    df = pd.read_csv('/Users/ytu-egemen-zeytinci/Desktop/sample_movies.csv')
    df = df.drop('score', axis=1)

    records = []
    future_to_id = {}

    count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for _, row in df.iterrows():
            submission = executor.submit(crawler.append, row['tconst'], row['primaryTitle'], row['startYear'])
            future_to_id[submission] = row['tconst']

        for future in concurrent.futures.as_completed(future_to_id):
            movie_id = future_to_id[future]
            try:
                count += 1
                if count % 1000 == 0:
                    print count
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (movie_id, exc))
            else:
                records.append(data + (movie_id,))

    df_img = pd.DataFrame(records, columns=['image_url', 'description', 'tconst'])
    df_all = df_img.merge(df, on='tconst')

    df_last = crawler.edit(df_all)

    db.insert(df_last)

if __name__ == '__main__':
    main()
