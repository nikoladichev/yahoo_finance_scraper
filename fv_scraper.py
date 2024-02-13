from finviz.helper_functions.request_functions import http_request_get
import json

STOCK_URL = "https://finviz.com/quote.ashx"
STOCK_PAGE = {}

def revenue_build(ticker):
    load_page(ticker, {"t": ticker, "ty": "rv"})
    page_parsed = STOCK_PAGE[ticker]

    title = page_parsed.cssselect('div[class="quote-header-wrapper"]')[0]
    keys = ["sector", "industry", "country", "exchange"]
    fields = [f.text_content() for f in title.cssselect('a[class="tab-link"]')]
    data = dict(zip(keys, fields))

    revenue = page_parsed.cssselect('script[id="route-init-data"]')[0];
    data["revenue_build"] = json.loads(revenue.text)

    return data

def load_page(ticker, payload):
    global STOCK_PAGE

    if ticker not in STOCK_PAGE:
        STOCK_PAGE[ticker], _ = http_request_get(
            url=STOCK_URL, payload=payload, parse=True
        )