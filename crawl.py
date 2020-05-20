from imdb.crawler import crawl
from imdb.data import insert
from util import parse_arguments


def main():
    arguments = parse_arguments()
    insert()
    crawl(arguments)


if __name__ == '__main__':
    main()
