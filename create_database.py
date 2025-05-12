import json
from tqdm import tqdm
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["places"]

def get_collection_name(cafe):
    if cafe.get("province"):
        return cafe["province"]
    address = cafe.get("location", "")
    if "تهران" in address:
        return "تهران"
    return "None"

if __name__ == "__main__":
    input_file = "cafe_ready.jsonl"

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in tqdm(lines, desc="Processing cafes"):
        try:
            cafe = json.loads(line)
        except json.JSONDecodeError:
            tqdm.write("[ERROR] Invalid JSON line")
            continue

        collection_name = get_collection_name(cafe)
        db[collection_name].insert_one(cafe)
        tqdm.write(f"[SAVED] {cafe['name']} → {collection_name}")
