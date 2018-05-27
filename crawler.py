import os
import time
import re
import sys
import json
import datetime
import collections
from pprint import pprint

import selenium
from selenium import webdriver


class BaseCrawler():
    headless_chromedriver_path = ""
    data_store_path = ""

    def __init__(self, index_path):
        self.index_path = index_path
        self.now = str(datetime.datetime.now())
        # init webdriver
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(
            chrome_options=option, executable_path=self.headless_chromedriver_path)
        self.driver.get(index_path)

    """開始爬取"""
    def crawl(self):
        driver = self.driver
        while self.isEnd(driver) == False:
            contents = self.getPageContent(self.driver)
            self.store(contents)
            self.driver = self.turnNextPage(driver)

        print('crawl end . time : from ' + self.now + ' to ' + str(datetime.datetime.now()))

    """取得本頁的資料"""
    def getPageContent(self, driver):
        pass

    """跳轉到下一頁"""
    def turnNextPage(self, driver):
        pass

    """儲存資料"""
    def store(self, data):
        pass

    """判斷是不是最後一頁了"""
    def isEnd(self, driver):
        print('BaseCrawler')
        pass


class RakuyaCrawler(BaseCrawler):
    """取得本頁的資料"""
    def getPageContent(self, driver):
        print('現在網址' + driver.current_url)
        output = []
        sections = driver.find_elements_by_css_selector(
            'div.obj-item')

        for section in sections:
            title = section.find_element_by_css_selector('div.obj-title').text
            url = section.find_element_by_css_selector('div.obj-title > h6 > a').get_attribute('href')
            prise = section.find_element_by_css_selector('li.obj-price').text
            address = section.find_element_by_css_selector('p.obj-address').text
            other = section.find_element_by_css_selector('ul.obj-data').text

            unit = {
                'title': title,
                'url': url,
                'prise': prise,
                'address': address,
                'other': other

            }
            output.append(unit)

        return output

    """跳轉到下一頁"""
    def turnNextPage(self, driver):
        try:
            base_url = self.base_url
            current_url = driver.current_url
            res = current_url.split(base_url)
            next_page = base_url + str(int(res[1]) + 1)

        except AttributeError:
            url = driver.find_element_by_css_selector(
                'body > div.container.obj-search-list.obj-search-rent.clearfix > div > div.content-main > nav > ul > li:nth-child(3) > a').get_attribute('href')
            self.base_url = url[:-1]
            base_url = url[:-1]
            next_page = url

        except selenium.common.exceptions.NoSuchElementException:
            print('the last page')
            sys.exit()

        except Exception as e:
            print(e)

        finally:
            driver.get(next_page)
            return driver

    """儲存資料"""
    def store(self, data):
        if not os.path.exists(self.data_store_path):
            os.mkdir(self.data_store_path)

        # 預設儲存檔名 Rakyya__DateTimeString.json
        file_path = self.data_store_path + 'Rakuya__' + self.now + '.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                json_old = json.load(f)
        else:
            json_old = {}

        for unit in data:
            json_old.update({len(json_old): unit})

        with open(file_path, 'w') as f:
            json.dump(json_old, f)

    """判斷是不是最後一頁了"""
    def isEnd(self, driver):
        # 最底頁按鈕
        last_bot = driver.find_element_by_css_selector(
                'body > div.container.obj-search-list.obj-search-rent.clearfix > div > div.content-main > nav > ul > li:nth-child(9)')
        isDisabled = last_bot.get_attribute('class')

        output = False

        if isDisabled == 'disabled':
            output = True

        return output


# class Rent591Crawler(BaseCrawler):
#     def crawler(self):

