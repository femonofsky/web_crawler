
from urllib.request import Request, urlopen, urljoin, URLError
from urllib.parse import urlparse


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import logging
import ssl
import time
from datetime import datetime, date


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

driver_path = '/Users/anp/Downloads/chromedriver'

browser = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
delay = 3 # seconds

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Crawler(object):
    """
        Class for Crawling Indonesia Stock Market Research
    """
    base_url = ''
    crawled_results = []

    def __init__(self, base_url):
        Crawler.base_url = base_url

    @staticmethod
    def crawl(url):
        """
            Crawl Companies details from URL
        :param url:
        :return:
        """
        try:
            logger.info("***************START******************")
            # start crawling from url
            browser.get(url)
            # Extract data from website
            Crawler.extract_data_from_page(browser)
            # close browser
            browser.close()
            logger.info("***************FINISH******************")
            return Crawler.crawled_results
        except URLError as e:
            logger.info("URL {} threw this error when trying to parse: {}".format(link, e.reason))
            return Crawler.crawled_results
        except Exception as e:
            print(e)
            return Crawler.crawled_results

    @staticmethod
    def extract_data_from_page(browser):
        """
            Extract Data From Table Data
        :param browser:
        :return:
        """
        table_data = []
        try:
            # waiting for "Table" to become visible
            table_data = WebDriverWait(browser, delay).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                '//*[@id="companyTable"]/tbody/tr')))
            logger.info("Page is ready!")
        except TimeoutException:
            logger.error("Loading took too much time!")
            print("Loading took too much time!")
        try:
            for company_data in table_data:
                Crawler.extract_data(company_data)
            try:
                # check if the pagination button is disabled
                browser.find_element(
                    By.CSS_SELECTOR, "#companyTable_paginate .paginate_button.next.disabled")
                logger.error("Last Data Set")
                print('Last Data Set')
                return
            except Exception as e:
                pass

            # click on the next button to load the paginated data
            browser.find_element_by_class_name('next').click()
            # wait for next paginated data to load
            time.sleep(delay)
            Crawler.extract_data_from_page(browser)
        except Exception as e:
            print(e)

    @staticmethod
    def extract_data(data):
        """
            Extract Companies Details
        :param data: list
        :return:
        """
        now = datetime.now()
        data_formatter = {}
        listing_date = data.find_elements_by_tag_name("td")[3].text
        # Format data
        data_formatter["ticker symbol"] = data.find_elements_by_tag_name("td")[1].text
        data_formatter["company name"] = data.find_elements_by_tag_name("td")[2].text
        data_formatter["listing_date"] = datetime.strptime(listing_date, "%d %b %Y").strftime("%Y-%m-%d")
        data_formatter["crawled_at"] = now.strftime("%Y-%m-%d")
        # Add new company details
        Crawler.crawled_results.append(data_formatter)


def append_to_csv(result):
    with open('../results.csv', 'a', newline=',') as csvfile:
        resultwriter = csv.writer(csvfile, delimiter=' ', quotechar='|')
        resultwriter.writerow(result)