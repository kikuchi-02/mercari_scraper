import os
import pickle
import re
import sys
import time
from argparse import ArgumentParser
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

# 必須
import chromedriver_binary
import pandas as pd
from pykakasi import kakasi, wakati
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


@contextmanager
def chrome():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def get_page_items(driver, strict: bool, keyword='') -> List[dict]:
    page_items = list()
    for item_box in driver.find_elements_by_class_name('items-box'):
        # なんか知らんけどemptyになりよる
        # title = item_box.find_element_by_class_name('items-box-name')
        title = item_box.find_element_by_css_selector('img').get_attribute(
            'alt')
        if strict and title.find(keyword) == -1:
            continue
        page_items.append({
            'title':
            title,
            'price':
            int(
                re.sub(
                    '¥|,', '',
                    item_box.find_element_by_class_name(
                        'items-box-price').text)),
            'is_sold_out':
            not item_box.find_elements_by_class_name('item-sold-out-badge'),
            'link':
            item_box.find_element_by_css_selector('a').get_attribute('href')
        })
    return page_items


def next_page() -> Optional['WebElement']:
    current_page = driver.find_element_by_css_selector(
        'li.pager-cell.active').text
    next_page_num = int(current_page) + 1
    try:
        elm = driver.find_element_by_link_text(str(next_page_num))
        return elm
    except NoSuchElementException:
        return None


def convert_roman_from_japanese(word: str) -> str:
    kakasi_ = kakasi()
    kakasi_.setMode("H", "a")  # Hiragana to ascii, default: no conversion
    kakasi_.setMode("K", "a")  # Katakana to ascii, default: no conversion
    kakasi_.setMode("J", "a")  # Japanese to ascii, default: no conversion
    kakasi_.setMode("r", "Hepburn")  # default: use Hepburn Roman table
    result = kakasi_.getConverter().do(args.word)
    result = result.replace(' ', '_').replace('　', '_')
    return result


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-m',
                        '--max',
                        type=int,
                        default=1000,
                        help='maximum records count')
    parser.add_argument('-w',
                        '--word',
                        type=str,
                        required=True,
                        help='search key word')
    parser.add_argument('-s',
                        '--strict',
                        action='store_true',
                        default=False,
                        help='wheather title must contains keyword')
    args = parser.parse_args()

    print(f'keyword: {args.word}')

    with chrome() as driver:
        driver.get('https://www.mercari.com/jp/')
        # search by keyword
        input_ = driver.find_element_by_xpath(
            '/html/body/div[1]/div/header/div/div[1]/form/input')
        input_.send_keys(args.word)
        input_.submit()
        # sort created desc
        time.sleep(3)
        driver.find_element_by_xpath(
            '/html/body/div[1]/main/div[2]/form/div[1]/div/div/select/option[4]'
        ).click()
        time.sleep(3)
        all_items = []
        while True:
            all_items.extend(get_page_items(driver, args.strict))
            next_page_elm = next_page()

            records_count: int = len(all_items)
            if records_count > args.max or not next_page_elm or int(
                    next_page_elm.text) > 50:
                break

            print(str(records_count) + 'count')
            print(f'next page: {next_page_elm.text}')

            next_page_elm.click()

        romaji = convert_roman_from_japanese(args.word)
        time_str = datetime.today().isoformat(timespec='minutes')
        df = pd.DataFrame.from_records(all_items)
        df.to_feather(f'{romaji}{time_str}.feather')
