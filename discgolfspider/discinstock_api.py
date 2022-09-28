import requests
from discgolfspider.items import DiscItem, CreateDiscItem
from scrapy.exceptions import CloseSpider, DropItem
from scrapy.utils.log import logger


class DiscinstockApi:
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url
        self.token = self.get_token(username, password)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_token(self, username: str, password: str) -> str:
        data = {"username": username, "password": password}
        response = requests.post(f"{self.api_url}/token", data=data)

        if response.status_code != 200:
            raise CloseSpider("Could not authenticate")

        token = response.json()["access_token"]
        return token

    def fetch_discs(self, spider_name: str):
        response = requests.get(f"{self.api_url}/discs/search?spider_name={spider_name}")

        if response.status_code != 200:
            raise CloseSpider("Could not fetch discs")

        discs: list = response.json()
        return discs

    def add_disc(self, disc: CreateDiscItem):
        response = requests.post(f"{self.api_url}/discs", json=disc.dict(), headers=self.headers)

        if response.status_code != 201:
            logger.error(f"{disc['spider_name']} | Could not add {disc['name']}({disc['url']}): {response.reason}")
            logger.debug(f"{response.content}")
            raise DropItem(f"Could not add {disc['name']}. Verify that the disc has all required fields.")

        added_disc: DiscItem = response.json()
        return added_disc

    def patch_disc(self, id: str, updates: dict):
        response = requests.patch(f"{self.api_url}/discs/{id}", json=updates, headers=self.headers)

        if response.status_code != 200:
            logger.error(f"Could not update {id}: {response.reason}")

        updated_disc: DiscItem = response.json()
        return updated_disc

    def search_disc(self, query: dict) -> list[DiscItem]:
        response = requests.get(f"{self.api_url}/discs/search", query)

        if response.status_code != 200:
            logger.error(f"Could not get disc by query ({query}): {response.reason}")

        discs: list = response.json()
        discs = [DiscItem(disc) for disc in discs]

        return discs
