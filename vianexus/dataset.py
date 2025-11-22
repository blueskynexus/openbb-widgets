import json
import httpx
import logging
from pydantic import BaseModel, Field
from config import settings


class StockStatsData(BaseModel):
    """Response schema for CORE/STOCK_STATS_US dataset"""

    week_52_change: float = Field(alias="52weekChange")
    week_52_high: float = Field(alias="52weekHigh")
    week_52_high_date: str = Field(alias="52weekHighDate")
    week_52_low: float = Field(alias="52weekLow")
    week_52_low_date: str = Field(alias="52weekLowDate")
    avg_30_day_volume: int = Field(alias="avg30DayVolume")
    beta: float
    date: str
    day_200_moving_average: float = Field(alias="day200MovingAverage")
    day_50_moving_average: float = Field(alias="day50MovingAverage")
    eps_ttm: float = Field(alias="epsTtm")
    issuer_name: str = Field(alias="issuerName")
    mic: str
    pe_ratio_ttm: float = Field(alias="peRatioTtm")
    shares_outstanding: int = Field(alias="sharesOutstanding")
    symbol: str
    ytd_change: float = Field(alias="ytdChange")
    id: str
    key: str
    subkey: str
    updated: float

    class Config:
        populate_by_name = True


class VnxQuoteData(BaseModel):
    """Response schema for EDGE/VNX_QUOTE dataset"""

    vnx_symbol: str = Field(alias="vnxSymbol")
    vnx_bid_size: int = Field(alias="vnxBidSize")
    vnx_bid_price: float = Field(alias="vnxBidPrice")
    vnx_ask_size: int = Field(alias="vnxAskSize")
    vnx_ask_price: float = Field(alias="vnxAskPrice")
    vnx_price: float = Field(alias="vnxPrice")
    vnx_last_sale_price: float = Field(alias="vnxLastSalePrice")
    vnx_last_sale_size: int = Field(alias="vnxLastSaleSize")
    vnx_low_price: float = Field(alias="vnxLowPrice")
    vnx_high_price: float = Field(alias="vnxHighPrice")
    vnx_open_price: float = Field(alias="vnxOpenPrice")
    vnx_close_price: float = Field(alias="vnxClosePrice")
    vnx_volume: int = Field(alias="vnxVolume")
    vnx_timestamp: int = Field(alias="vnxTimestamp")
    vnx_market_percent: float = Field(alias="vnxMarketPercent")
    vnx_high_time: int = Field(alias="vnxHighTime")
    vnx_low_time: int = Field(alias="vnxLowTime")
    vnx_price_type: str = Field(alias="vnxPriceType")
    market_volume: int | None = Field(alias="MarketVolume", default=None)

    class Config:
        populate_by_name = True


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

    def data(self, symbols: list[str], last: int = 1):
        """Get historical data for the dataset for the given symbols

        Args:
            symbols: List of stock symbols
            last: Number of historical records to fetch (default: 30 for ~1 month)
        """
        data = self.make_request(symbols, last=last)
        logging.debug(f"Data: \n{json.dumps(data, indent=4)}")
        return data


class StockStats(Dataset):
    def __init__(self):
        super().__init__("CORE", "STOCK_STATS_US")

    def data(self, symbols: list[str], last: int = 1) -> list[StockStatsData]:
        """Get stock statistics data with validated schema

        Args:
            symbols: List of stock symbols
            last: Number of historical records to fetch (default: 1)

        Returns:
            List of validated StockStatsData objects
        """
        raw_data = super().data(symbols, last=last)
        return [StockStatsData(**item) for item in raw_data]


class VnxQuote(Dataset):
    def __init__(self):
        super().__init__("EDGE", "VNX_QUOTE")

    def data(self, symbols: list[str], last: int = 1) -> list[VnxQuoteData]:
        """Get VNX quote data with validated schema

        Args:
            symbols: List of stock symbols
            last: Number of historical records to fetch (default: 1)

        Returns:
            List of validated VnxQuoteData objects
        """
        raw_data = super().data(symbols, last=last)
        return [VnxQuoteData(**item) for item in raw_data]


stock_stats = StockStats()
vnx_quote = VnxQuote()
