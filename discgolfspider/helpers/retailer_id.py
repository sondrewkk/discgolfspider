import hashlib

def create_retailer_id(brand: str, url: str) -> str:
    if not brand or not url:
        raise ValueError()

    id = f"{url}{brand}".encode()
    hashed_id = hashlib.md5(id).hexdigest()

    return hashed_id