
import scrapy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime, date
import logging


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

driver_path = '/Users/anp/Downloads/chromedriver'
delay = 3 # seconds


class CompanySpider(scrapy.Spider):
    name = "company_spider"
    allowed_domains = ['idx.co.id']
    start_urls = ['https://www.idx.co.id/en-us/listed-companies/company-profiles/']

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    def parse(self, response):
        self.driver.get(response.url)

        while True:
            logging.info("Load Table Data")
            # waiting for "Table" to become visible
            try:
                table_data = WebDriverWait(self.driver, delay).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                  '//*[@id="companyTable"]/tbody/tr')))
            except:
                logging.error("Loading took too much time!")
                break
            # process each row
            for company_data in table_data:
                now = datetime.now()
                data_formatter = {}

                listing_date = company_data.find_elements_by_tag_name("td")[3].text
                company_title = company_data.find_elements_by_tag_name("td")[2]
                # Format data
                data_formatter["ticker symbol"] = company_data.find_elements_by_tag_name("td")[1].text
                data_formatter["company_name"] = company_title.text
                data_formatter["url"] = company_title.find_element_by_css_selector('a').get_attribute("href")
                data_formatter["listing_date"] = datetime.strptime(listing_date, "%d %b %Y").strftime("%Y-%m-%d")
                data_formatter["crawled_at"] = now.strftime("%Y-%m-%d")
                yield data_formatter
                logging.info('Crawled'+str(data_formatter))
            next = self.driver.find_element_by_class_name('next')
            try:
                # check if the pagination button is disabled
                self.driver.find_element(
                    By.CSS_SELECTOR, "#companyTable_paginate .paginate_button.next.disabled")
                logging.error("last data")
                break
                # get the data and write it to scrapy items
            except:
                # click on the next button to load the paginated data
                next.click()
                logging.info("Next button Clicked")
                # wait for next paginated data to load
                time.sleep(delay)
        logging.info("Browser closed")
        # close browser
        self.driver.close()
