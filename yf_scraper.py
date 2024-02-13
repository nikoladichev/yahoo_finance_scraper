import string
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from enum import Enum
from lxml import html, etree
from user_agent import generate_user_agent


class YfSection(Enum):
    SUMMARY = ('', lambda symbol: scrape_summary(symbol))
    STATISTICS = ('/key-statistics', lambda symbol: scrape_statistics(symbol))
    HISTORICAL_DATA = ('/history', lambda symbol: scrape_historical_data(symbol))
    PROFILE = ('/profile', lambda symbol: scrape_profile(symbol))
    FINANCIALS_INCOME_STATEMENT_ANNUAL = (
        '/financials', lambda symbol: scrape_income_statement_annual(symbol))
    FINANCIALS_INCOME_STATEMENT_QUARTERLY = (
        '/financials', lambda symbol: scrape_income_statement_quarterly(symbol))  # FIXME
    FINANCIALS_INCOME_BALANCE_SHEET_ANNUAL = (
        '/balance-sheet', lambda symbol: scrape_balance_sheet_annual(symbol))
    FINANCIALS_INCOME_BALANCE_SHEET_QUARTERLY = (
        '/balance-sheet', lambda symbol: scrape_balance_sheet_quarterly(symbol))  # FIXME
    FINANCIALS_CASH_FLOW_ANNUAL = (
        '/cash-flow', lambda symbol: scrape_cash_flow_annual(symbol))
    FINANCIALS_CASH_FLOW_QUARTERLY = (
        '/cash-flow', lambda symbol: scrape_cash_flow_quarterly(symbol))  # FIXME
    ANALYSIS = ('/analysis', lambda symbol: scrape_analysis(symbol))
    OPTIONS = ('/options', lambda symbol: scrape_options(symbol))
    HOLDERS = ('/holders', lambda symbol: scrape_holders(symbol))
    SUSTAINABILITY = ('/sustainability', lambda symbol: scrape_sustainability(symbol))


STOCK_PAGE = {}


def load_page(symbol: string, section: YfSection, parse=True):
    global STOCK_PAGE

    url = f'https://finance.yahoo.com/quote/{symbol}{section.value[0]}'
    params = {"_guc_consent_skip": int(time.time())}
    user_agent = generate_user_agent()

    if symbol not in STOCK_PAGE:
        STOCK_PAGE[symbol] = requests.get(
            url=url,
            params=params,
            verify=False,
            headers={"User-Agent": user_agent})

    content = STOCK_PAGE[symbol]

    if parse:
        return html.fromstring(content.text), content.url
    else:
        return content.text, content.url


def yf_stock_data(symbol: string, section: YfSection):
    page_html = load_page(symbol, section, True)[0]
    return section.value[1](page_html)

def scrape_summary(symbol: string):
    raise NotImplementedError("Summary API is not implemented yet")


def scrape_statistics(symbol: string):
    raise NotImplementedError("Statistics API is not implemented yet")


def scrape_historical_data(symbol: string):
    raise NotImplementedError("Historical Data API is not implemented yet")


def scrape_profile(symbol: string):
    raise NotImplementedError("Profile API is not implemented yet")


def scrape_income_statement_annual(symbol: string):
    raise NotImplementedError("Income Statement API is not implemented yet")


def scrape_income_statement_quarterly(symbol: string):
    raise NotImplementedError("Income Statement API is not implemented yet")


def scrape_balance_sheet_annual(symbol: string):
    raise NotImplementedError("Balance Sheet API is not implemented yet")


def scrape_balance_sheet_quarterly(symbol: string):
    raise NotImplementedError("Balance Sheet API is not implemented yet")


def scrape_cash_flow_annual(symbol: string):
    raise NotImplementedError("Cash Flow API is not implemented yet")


def scrape_cash_flow_quarterly(symbol: string):
    raise NotImplementedError("Cash Flow API is not implemented yet")



def scrape_analysis(page_parsed):
    analysis = {}

    section = page_parsed.cssselect('section[data-test="qsp-analyst"]')[0]
    analysis['currency'] = section.cssselect('div')[0].text_content().replace("Currency in ", "")

    tables = section.cssselect('table')

    for table in tables:
        headers = table.cssselect('thead th')
        dict = {}
        for i in range(1, len(headers)):
            rows = table.cssselect('tbody tr')
            data = {}
            for row in rows:
                prop = (row.cssselect('td')[0].text_content().lower()
                        .replace(" ", "_")
                        .replace(".", "")
                        .replace("(", "")
                        .replace(")", "")
                        .replace("%", "percent")
                        .replace("/", "_over_"))
                val = row.cssselect('td')[i].text_content()

                if is_numeric(val):
                    val = round(float(val), 2)
                elif val.endswith("M"):
                    val = int(float(val.replace("M", "")) * 1000000)
                elif val.endswith("B"):
                    val = int(float(val.replace("B", "")) * 1000000000)
                elif "N/A" == val:
                    val = None
                elif val.endswith("%"):
                    val = round(float(val.replace("%", "")) / 100, 2)

                data[prop] = val
            dict[headers[i].text_content().lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "")] = data

        analysis[headers[0].text_content().lower().replace(" ", "_")] = dict

    return analysis



def scrape_analysis_selenium(symbol):
    # build the URL of the target page
    url = f'https://finance.yahoo.com/quote/{symbol}/analysis'

    # initialize a web driver instance to control a Chrome window
    options = Options()
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    try:
        # set up the window size of the controlled browser
        driver.set_window_size(1920, 1080)

        # visit the target page
        driver.get(url)

        # wait up to 3 seconds for the consent modal to show up
        consent_overlay = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.consent-overlay')))

        # click the "Accept all" button
        accept_all_button = consent_overlay.find_element(By.CSS_SELECTOR, '.accept-all')
        accept_all_button.click()

        analysis = {}
        analysis['currency'] = driver.find_element(By.CSS_SELECTOR, '[data-test="qsp-analyst"]').find_element(
            By.TAG_NAME,
            'span').text.replace(
            "Currency in ", "")

        tables = driver.find_element(By.CSS_SELECTOR, '[data-test="qsp-analyst"]').find_elements(By.TAG_NAME, 'table')

        for table in tables:
            headers = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
            dict = {}
            for i in range(1, len(headers)):
                rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                data = {}
                for row in rows:
                    prop = (row.find_elements(By.TAG_NAME, 'td')[0].text.lower()
                            .replace(" ", "_")
                            .replace(".", "")
                            .replace("(", "")
                            .replace(")", "")
                            .replace("%", "percent")
                            .replace("/", "_over_"))
                    val = row.find_elements(By.TAG_NAME, 'td')[i].text

                    if is_numeric(val):
                        val = round(float(val), 2)
                    elif val.endswith("M"):
                        val = int(float(val.replace("M", "")) * 1000000)
                    elif val.endswith("B"):
                        val = int(float(val.replace("B", "")) * 1000000000)
                    elif "N/A" == val:
                        val = None
                    elif val.endswith("%"):
                        val = round(float(val.replace("%", "")) / 100, 2)

                    data[prop] = val
                dict[
                    headers[i].text.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "")] = data

            analysis[headers[0].text.lower().replace(" ", "_")] = dict

            return analysis

    except TimeoutException:
        print('Cookie consent overlay missing')

    finally:
        # close the browser and free up the resources
        driver.quit()

def scrape_options(symbol: string):
    raise NotImplementedError("Options API is not implemented yet")


def scrape_holders(symbol: string):
    raise NotImplementedError("Holders API is not implemented yet")


def scrape_sustainability(symbol: string):
    raise NotImplementedError("Sustainability API is not implemented yet")


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
