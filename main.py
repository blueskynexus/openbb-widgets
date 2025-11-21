import util.configure_logging as util
from via_nexus.dataset import stock_stats, vnx_quote

def main():
    util.configure_logging()

    stock_data = stock_stats.data(["AAPL"])
    if len(stock_data) == 0:
        raise ValueError("No data found for the given symbols")

    vnx_quote_data = vnx_quote.data(["AAPL"])
    if len(vnx_quote_data) == 0:
        raise ValueError("No data found for the given symbols")

if __name__ == "__main__":
    main()
