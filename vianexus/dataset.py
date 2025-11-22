import json
import httpx
import logging
from config import settings


class Dataset:
    def __init__(self, namespace: str, dataset: str):
        self.base_url = settings.vianexus_base_url
        self.api_key = settings.vianexus_api_key
        self.namespace = namespace
        self.dataset = dataset

    def make_request(self, symbols: list[str], last: int = 1):
        """Make a request to the Vianexus API to get the data for the dataset for the given symbols"""
        url = f"{self.base_url}/data/{self.namespace}/{self.dataset}/{','.join(symbols)}"
        params = {
            "token": self.api_key,
            "last": last,
        }
        response = httpx.get(url, params=params, timeout=10)
        return response.json()

    def data(self, symbols: list[str]):
        """Get the data for the dataset for the given symbols"""
        data = self.make_request(symbols, last=1)
        logging.debug(f"Data: \n{json.dumps(data, indent=4)}")
        return data

    def historical_data(self, symbols: list[str], last: int = 30):
        """Get historical data for the dataset for the given symbols

        Args:
            symbols: List of stock symbols
            last: Number of historical records to fetch (default: 30 for ~1 month)
        """
        data = self.make_request(symbols, last=last)
        logging.debug(f"Historical Data: \n{json.dumps(data, indent=4)}")
        return data


stock_stats = Dataset("CORE", "STOCK_STATS_US")
"""
[
  {
    "52weekChange": -0.19,
    "52weekHigh": 312.56,
    "52weekHighDate": "2025-01-30",
    "52weekLow": 201.68,
    "52weekLowDate": "2025-04-07",
    "avg30DayVolume": 180729,
    "beta": 0.87,
    "date": "2025-11-21",
    "day200MovingAverage": 240.85,
    "day50MovingAverage": 237.55,
    "epsTtm": 28.52,
    "issuerName": "Asbury Automotive Group Inc",
    "mic": "XNYS",
    "peRatioTtm": 7.69,
    "sharesOutstanding": 19440558,
    "symbol": "ABG",
    "ytdChange": -0.11,
    "id": "STOCK_STATS_US",
    "key": "ABG",
    "subkey": "",
    "updated": 1763730632006.439
  }
]
"""

vnx_quote = Dataset("EDGE", "VNX_QUOTE")
"""
[
  {
    "vnxSymbol": "AAPL",
    "vnxBidSize": 100,
    "vnxBidPrice": 271.5,
    "vnxAskSize": 100,
    "vnxAskPrice": 271.49,
    "vnxPrice": 271.4947,
    "vnxLastSalePrice": 271.4822,
    "vnxLastSaleSize": 362,
    "vnxLowPrice": 266.2595,
    "vnxHighPrice": 273.3009,
    "vnxOpenPrice": 0,
    "vnxClosePrice": 0,
    "vnxVolume": 1007,
    "vnxTimestamp": 1763758911098,
    "vnxMarketPercent": 0,
    "vnxHighTime": 1763752863134,
    "vnxLowTime": 1763735403225,
    "vnxPriceType": "U",
    "MarketVolume": null
  }
]
"""
