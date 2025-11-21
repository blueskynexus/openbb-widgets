import os
import json
import yaml
import httpx
from dotenv import load_dotenv

load_dotenv()

class Dataset:
    def __init__(self, base_url: str, namespace: str, dataset: str):
        self.base_url = base_url
        self.namespace = namespace
        self.dataset = dataset
        self.api_key = os.getenv("VIANEXUS_API_KEY_PROD")

    def data(self, symbols: list[str]):
        '''Make a request to the Vianexus API to get the data for the dataset for the given symbols'''
        url = f"{self.base_url}/data/{self.namespace}/{self.dataset}/{','.join(symbols)}"
        params = {
            "token": self.api_key,
            "last": 1,
        }
        response = httpx.get(url, params=params, timeout=10)
        return response.json()


def main():
    yaml_config = yaml.load(open("config.yaml"), Loader=yaml.FullLoader)
    config = yaml_config[os.getenv("ENVIRONMENT")]
    stock_stats_us = Dataset(config["vianexus_base_url"], "CORE", "STOCK_STATS_US")
    stock_data = stock_stats_us.data(["AAPL"])
    print(json.dumps(stock_data, indent=4))

    vnx_quote = Dataset(config["vianexus_base_url"], "EDGE", "VNX_QUOTE")
    vnx_quote_data = vnx_quote.data(["AAPL"])
    print(json.dumps(vnx_quote_data, indent=4))

if __name__ == "__main__":
    main()
