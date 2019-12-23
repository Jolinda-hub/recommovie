from imdb.crawler import crawl, db, util


def main():
    arguments = util.parse_arguments()

    # crawl movies
    df_last = crawl(arguments)

    # insert to db
    db.insert(df_last)


if __name__ == '__main__':
    main()
