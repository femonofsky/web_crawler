from crawler import *
import csv


def main():
    base_url = 'https://www.idx.co.id/en-us/listed-companies/company-profiles/'
    Crawler.crawl(base_url)


if __name__ == '__main__':
    main()