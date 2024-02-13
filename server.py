import string

from flask import Flask, jsonify
from yf_scraper import yf_stock_data, YfSection
from fv_scraper import revenue_build

app = Flask(__name__)

@app.route("/")
def alive():
    return "Scraper is up!", 200

@app.route("/<ticker_symbol>/analysis")
def scrape_summary(ticker_symbol: string):
    return jsonify(yf_stock_data(ticker_symbol, YfSection.ANALYSIS)), 200

@app.route("/<ticker_symbol>/revenue-build")
def scrape_revenue_build(ticker_symbol: string):
    return jsonify(revenue_build(ticker_symbol))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)
    # app.run(host='0.0.0.0', port=9090)