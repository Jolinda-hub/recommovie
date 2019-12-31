from db.data_opt import DataOperation
from imdb.crawler import crawl, util


def main():
    db = DataOperation()
    arguments = util.parse_arguments()

    # crawl movies
    df_last = crawl(arguments)

    # insert to db
    db.insert(df_last)


if __name__ == '__main__':
    main()
