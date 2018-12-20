
import scrapy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime, date
import logging
import json


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')

driver_path = '/Users/anp/Downloads/chromedriver'
delay = 3 # seconds


class CompanyProfileSpider(scrapy.Spider):

    name = "company_profile_spider"
    allowed_domains = ['idx.co.id']
    start_urls = []

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)

    def start_requests(self):
        logging.info("Loading Urls from company_index.json")
        try:
            # load url from company_index.json
            with open("company_index.json", 'r') as infile:
                list_of_companies = json.load(infile)
                for company_url in list_of_companies:
                    if 'url' in company_url:
                        yield scrapy.Request(url=company_url['url'], callback=self.parse, dont_filter=True)
        except Exception as e:
            logging.error(e)
            logging.error("No such file or directory ")

    def parse(self, response):
        """
            Process Each URL
        :param response:
        :return:
        """
        self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        self.driver.get(response.url)
        try:
            # waiting for page content to become visible
            general = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, 'general')))
            result = {}
            result['Company Name'] = extract_data_by_id(general, 'frName')
            result['Security Code'] = extract_data_by_id(general, 'frSecurityCode')
            result['Office address'] = extract_data_by_id(general, 'frOfficeAddress')
            result['Email Address'] = extract_data_by_id(general, 'frEmail')
            result['Country'] = "Indonesia"
            result['Phone'] = extract_data_by_id(general, 'frTelephone')
            result['Fax'] = extract_data_by_id(general, 'frFax')
            result['NPWP'] = extract_data_by_id(general, 'frNpwp')
            result['Company Website'] = extract_data_by_id(general, 'frWebsite')
            result['IPO Date'] = extract_data_by_id(general, 'frIpoDate')
            result['Board'] = extract_data_by_id(general, 'frBoard')
            result['Sector'] = extract_data_by_id(general, 'frSector')
            result['Sub Sector'] = extract_data_by_id(general, 'frSubSector')
            result['Registrar'] = extract_data_by_id(general, 'frBAE')
            result['Corporate Secretary'] = extract_data_from_table(general, 'csTable', ['name', 'email', 'phone'])
            result['Director'] = extract_data_from_table(general, 'directorTable', ['name', 'position'])
            result['Subsidiary'] = extract_data_from_table(general, 'subsidiaryTable_wrapper', ['name', 'type',
                                                                                    'total asset', 'percentage'])
            self.driver.close()

            yield result

        except Exception as e:
            logging.error(e)
            logging.error("Loading took too much time!")
            self.driver.close()
            return


def extract_data_by_id(element, name):
    """
        Extract Data by Element ID
    :param element:
    :param name:
    :return:
    """
    try:
        return element.find_element_by_id(name).text
    except:
        return ''


def extract_data_by_tag_name(element, name, index):
    """
        Extract Data from Element by tag name
    :param element:
    :param name:
    :param index:
    :return:
    """
    try:
        return element.find_elements_by_tag_name(name)[index].text
    except:
        return ''


def extract_data_from_table(driver, table_id, col=[]):
    """
        Extract Data From Table
    :param driver:
    :param table_id:
    :param col:
    :return:
    """
    result_list = []
    while True:
        try:
            _row = driver.find_elements(By.CSS_SELECTOR, "#"+table_id+" tbody tr")
            for data in _row:
                hold = {}
                index = 0
                for item in col:
                    hold[item] = extract_data_by_tag_name(data, 'td', index)
                    index = index+1
                    logging.error(hold)
                result_list.append(hold)
            try:
                # check if the pagination button is disabled
                driver.find_element(By.CSS_SELECTOR, "#"+table_id+" .paginate_button.next.disabled")
                logging.error("last data")
                break
                # get the data and write it to scrapy items
            except:
                next = driver.find_element(By.CSS_SELECTOR, "#" + table_id + " .paginate_button.next")
                # click on the next button to load the paginated data
                next.click()
                logging.info("Next button Clicked")
                # wait for next paginated data to load
                time.sleep(delay)
        except Exception as e:
            logging.error(e)
            return result_list
    return result_list