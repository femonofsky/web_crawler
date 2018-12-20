#  Web Crawler
 Web Crawler gathers and categories information on the World Wide Web (WWW)
Data Scraping(Data Extraction) on the other hand refers to 
retrieving information from any source (not necessarily the web).

## Requirements
* Python 3.4+
* Works on Linux, Windows, Mac OSX, BSD


### Installing

Install dependence 
```
pip install -r requirements.txt
```

### Run
To Get all Companies Url
```
scrapy runspider company_spider.py -o company_index.json
```

To Gell 
company_profiles.json
```
scrapy runspider company_spider.py -o company_profiles.json
```