import json
import re
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import unquote


client = MongoClient("mongodb://localhost:27017/")
db = client["places"]

def is_persian_url(url):
    decoded = unquote(url)
    return bool(re.search(r'[\u0600-\u06FF]', decoded))

def is_valid_cafe(cafe):
    return (
        cafe.get("name") is not None and
        cafe.get("location") is not None and
        cafe.get("attributes")
    )

def get_collection_name(cafe):
    if cafe.get("city"):
        return cafe["city"]
    address = cafe.get("location", "")
    if "تهران" in address:
        return "تهران"
    return "None"

if __name__ == "__main__":
    input_file = "cafe_data.jsonl"

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in tqdm(lines, desc="Processing cafes"):
        try:
            cafe = json.loads(line)
        except json.JSONDecodeError:
            tqdm.write("[ERROR] Invalid JSON line")
            continue

        url = cafe.get("url", "")
        if is_persian_url(url):
            tqdm.write(f"[SKIPPED] Persian URL: {url}")
            continue

        if not is_valid_cafe(cafe):
            tqdm.write(f"[INVALID] Missing required fields: {url}")
            continue

        collection_name = get_collection_name(cafe)
        db[collection_name].insert_one(cafe)
        tqdm.write(f"[SAVED] {cafe['name']} → {collection_name}")
