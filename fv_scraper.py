from finviz.helper_functions.request_functions import http_request_get
import json

STOCK_URL = "https://finviz.com/quote.ashx"
STOCK_PAGE = {}

def revenue_build(ticker):
    load_page(ticker, {"t": ticker, "ty": "rv"})
    page_parsed = STOCK_PAGE[ticker]

    title = page_parsed.cssselect('div[class="quote-header-wrapper"]')[0]
    keys = ["Company", "Sector", "Industry", "Country"]
    fields = [f.text_content() for f in title.cssselect('a[class="tab-link"]')]
    data = dict(zip(keys, fields))

    revenue = page_parsed.cssselect('script[id="route-init-data"]')[0];
    data["Revenue"] = json.loads(revenue.text)

    #
    # all_rows = [
    #     row.xpath("td//text()")
    #     for row in page_parsed.cssselect('tr[class="table-dark-row"]')
    # ]
    #
    # for row in all_rows:
    #     for column in range(0, 11, 2):
    #         if row[column] == "EPS next Y" and "EPS next Y" in data.keys():
    #             data["EPS growth next Y"] = row[column + 1]
    #             continue
    #         elif row[column] == "Volatility":
    #             vols = row[column + 1].split()
    #             data["Volatility (Week)"] = vols[0]
    #             data["Volatility (Month)"] = vols[1]
    #             continue
    #
    #         data[row[column]] = row[column + 1]

    return data

def load_page(ticker, payload):
    global STOCK_PAGE

    if ticker not in STOCK_PAGE:
        STOCK_PAGE[ticker], _ = http_request_get(
            url=STOCK_URL, payload=payload, parse=True
        )