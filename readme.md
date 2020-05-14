# Scraper for mercari

You can get mercari items' data, using Selenium. This scraper helps you to know how much and how many masks are sold.

## dependencies
- Python 3.7.7

Use your suitable chrome-driver

## Usage

max(default is 1000): maximum number of records

word(necessary): search keyword

strict(default is False): whether title must contains search keyword

Example
```py
python scraper.py --max 100 --word 'マスク' --strict
```

The scraped data will be converted into pandas DataFrame. DataFrame is saved in feather format file, which suitable for this scraper. Although the feather format has some constrains, the format makes it faster to save and read file.

The saved file is named `{romanized search_keyword}.py`. The search keyword is romanized by pykakasi.