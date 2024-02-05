import string

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from enum import Enum

class Section(Enum):
    SUMMARY = ('', lambda driver, ticker_symbol: scrape_summary(driver, ticker_symbol))
    STATISTICS = ('/key-statistics', lambda driver, ticker_symbol: scrape_statistics(driver, ticker_symbol))
    HISTORICAL_DATA = ('/history', lambda driver, ticker_symbol: scrape_statistics(driver, ticker_symbol))
    PROFILE = ('/profile', lambda driver, ticker_symbol: scrape_profile(driver, ticker_symbol))
    FINANCIALS_INCOME_STATEMENT_ANNUAL = ('/financials', lambda driver, ticker_symbol: scrape_income_statement_annual(driver, ticker_symbol))
    FINANCIALS_INCOME_STATEMENT_QUARTERLY = ('/financials', lambda driver, ticker_symbol: scrape_income_statement_quarterly(driver, ticker_symbol)) # FIXME
    FINANCIALS_INCOME_BALANCE_SHEET_ANNUAL = ('/balance-sheet', lambda driver, ticker_symbol: scrape_balance_sheet_annual(driver, ticker_symbol))
    FINANCIALS_INCOME_BALANCE_SHEET_QUARTERLY = ('/balance-sheet', lambda driver, ticker_symbol: scrape_balance_sheet_quarterly(driver, ticker_symbol)) # FIXME
    FINANCIALS_CASH_FLOW_ANNUAL = ('/cash-flow', lambda driver, ticker_symbol: scrape_cash_flow_annual(driver, ticker_symbol))
    FINANCIALS_CASH_FLOW_QUARTERLY = ('/cash-flow', lambda driver, ticker_symbol: scrape_cash_flow_quarterly(driver, ticker_symbol)) # FIXME
    ANALYSIS = ('/analysis', lambda driver, ticker_symbol: scrape_analysis(driver, ticker_symbol))
    OPTIONS = ('/options', lambda driver, ticker_symbol: scrape_options(driver, ticker_symbol))
    HOLDERS = ('/holders', lambda driver, ticker_symbol: scrape_holders(driver, ticker_symbol))
    SUSTAINABILITY = ('/sustainability', lambda driver, ticker_symbol: scrape_sustainability(driver, ticker_symbol))

def scrape_stock_data(ticker_symbol: string, section: Section):
    # build the URL of the target page
    url = f'https://finance.yahoo.com/quote/{ticker_symbol}{section.value[0]}'

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

        return section.value[1](driver, ticker_symbol)

    except TimeoutException:
        print('Cookie consent overlay missing')

    finally:
        # close the browser and free up the resources
        driver.quit()


def scrape_summary(driver, ticker_symbol):
    regular_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketPrice"]') \
        .text
    regular_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChange"]') \
        .text
    regular_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')
    post_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketPrice"]') \
        .text
    post_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChange"]') \
        .text
    post_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="postMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')
    previous_close = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PREV_CLOSE-value"]').text
    open_value = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="OPEN-value"]').text
    bid = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BID-value"]').text
    ask = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="ASK-value"]').text
    days_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DAYS_RANGE-value"]').text
    week_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="FIFTY_TWO_WK_RANGE-value"]').text
    volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="TD_VOLUME-value"]').text
    avg_volume = driver.find_element(By.CSS_SELECTOR,
                                     '#quote-summary [data-test="AVERAGE_VOLUME_3MONTH-value"]').text
    market_cap = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="MARKET_CAP-value"]').text
    beta = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BETA_5Y-value"]').text
    pe_ratio = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PE_RATIO-value"]').text
    eps = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EPS_RATIO-value"]').text
    earnings_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EARNINGS_DATE-value"]').text
    dividend_yield = driver.find_element(By.CSS_SELECTOR,
                                         '#quote-summary [data-test="DIVIDEND_AND_YIELD-value"]').text
    ex_dividend_date = driver.find_element(By.CSS_SELECTOR,
                                           '#quote-summary [data-test="EX_DIVIDEND_DATE-value"]').text
    year_target_est = driver.find_element(By.CSS_SELECTOR,
                                          '#quote-summary [data-test="ONE_YEAR_TARGET_PRICE-value"]').text

    # initialize the dictionary
    stock = {}
    stock['regular_market_price'] = regular_market_price
    stock['regular_market_change'] = regular_market_change
    stock['regular_market_change_percent'] = regular_market_change_percent
    stock['post_market_price'] = post_market_price
    stock['post_market_change'] = post_market_change
    stock['post_market_change_percent'] = post_market_change_percent
    stock['previous_close'] = previous_close
    stock['open_value'] = open_value
    stock['bid'] = bid
    stock['ask'] = ask
    stock['days_range'] = days_range
    stock['week_range'] = week_range
    stock['volume'] = volume
    stock['avg_volume'] = avg_volume
    stock['market_cap'] = market_cap
    stock['beta'] = beta
    stock['pe_ratio'] = pe_ratio
    stock['eps'] = eps
    stock['earnings_date'] = earnings_date
    stock['dividend_yield'] = dividend_yield
    stock['ex_dividend_date'] = ex_dividend_date
    stock['year_target_est'] = year_target_est
    return stock

def scrape_statistics(driver, ticker_symbol):
    raise NotImplementedError("Statistics API is not implemented yet")

def scrape_historical_data(driver, ticker_symbol):
    raise NotImplementedError("Historical Data API is not implemented yet")

def scrape_profile(driver, ticker_symbol):
    raise NotImplementedError("Profile API is not implemented yet")

def scrape_income_statement_annual(driver, ticker_symbol):
    raise NotImplementedError("Income Statement API is not implemented yet")

def scrape_income_statement_quarterly(driver, ticker_symbol):
    raise NotImplementedError("Income Statement API is not implemented yet")

def scrape_balance_sheet_annual(driver, ticker_symbol):
    raise NotImplementedError("Balance Sheet API is not implemented yet")

def scrape_balance_sheet_quarterly(driver, ticker_symbol):
    raise NotImplementedError("Balance Sheet API is not implemented yet")

def scrape_cash_flow_annual(driver, ticker_symbol):
    raise NotImplementedError("Cash Flow API is not implemented yet")

def scrape_cash_flow_quarterly(driver, ticker_symbol):
    raise NotImplementedError("Cash Flow API is not implemented yet")

def scrape_analysis(driver, ticker_symbol):

    analysis = {}
    analysis['currency'] = driver.find_element(By.CSS_SELECTOR, '[data-test="qsp-analyst"]').find_element(By.TAG_NAME, 'span').text.replace("Currency in ", "")

    tables = driver.find_element(By.CSS_SELECTOR, '[data-test="qsp-analyst"]').find_elements(By.TAG_NAME, 'table')

    for table in tables:
        headers = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
        for i in range(1, len(headers)):
            rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
            data = {}
            for row in rows:
                prop = row.find_elements(By.TAG_NAME, 'td')[0].text.lower().replace(" ", "_").replace(".", "")
                data[prop] = row.find_elements(By.TAG_NAME, 'td')[i].text
            analysis[headers[0].text.lower().replace(" ", "_")] = data

    return analysis
def scrape_options(driver, ticker_symbol):
    raise NotImplementedError("Options API is not implemented yet")

def scrape_holders(driver, ticker_symbol):
    raise NotImplementedError("Holders API is not implemented yet")

def scrape_sustainability(driver, ticker_symbol):
    raise NotImplementedError("Sustainability API is not implemented yet")