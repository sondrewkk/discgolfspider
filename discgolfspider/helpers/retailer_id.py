import hashlib
from scrapy.utils.log import logger

def create_retailer_id(brand: str, url: str) -> str:
    if not brand or not url:
        return None

    logger.debug(f"{brand=} | {url=}")

    id = f"{url}{brand}".encode()
    hashed_id = hashlib.md5(id).hexdigest()

    return hashed_id