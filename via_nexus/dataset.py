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

    def make_request(self, symbols: list[str]):
        '''Make a request to the Vianexus API to get the data for the dataset for the given symbols'''
        url = f"{self.base_url}/data/{self.namespace}/{self.dataset}/{','.join(symbols)}"
        params = {
            "token": self.api_key,
            "last": 1,
        }
        response = httpx.get(url, params=params, timeout=10)
        return response.json()
    
    def data(self, symbols: list[str]):
        '''Get the data for the dataset for the given symbols'''
        data = self.make_request(symbols)
        logging.debug(f"Data: \n{json.dumps(data, indent=4)}")
        return data

stock_stats = Dataset("CORE", "STOCK_STATS_US")
vnx_quote = Dataset("EDGE", "VNX_QUOTE")
