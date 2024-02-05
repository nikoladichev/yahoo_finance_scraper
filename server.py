from flask import Flask, jsonify
from yf_scraper import scrape_stock_data, Section

app = Flask(__name__)

@app.route("/")
def alive():
    return "Scraper is up!", 200

@app.route("/<ticker_symbol>/analysis")
def scrape_summary(ticker_symbol):
    return jsonify(scrape_stock_data(ticker_symbol, Section.ANALYSIS)), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)
    # app.run(host='0.0.0.0', port=9090)