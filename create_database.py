import os
import json
from tqdm import tqdm
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["places"]

def get_collection_name(cafe):
    if cafe.get("province"):
        return cafe["province"]
    address = cafe.get("location", "")
    if "تهران" in address:
        return "تهران"
    return "None"

def process_cafe_data(cafe):
    # Keys to remove
    keys_to_remove = {
        "جای پارک", "غذا", "غذای گیاهی", "رزرو تلفنی", "بیرون‌بر",
        "مناسب برای قرار دونفره", "مناسب برای قرار گروهی",  "کتابخانه",
        "مناسب برای خانواده", "مناسب برای کودکان", "دلیوری(تحویل در محل)",
    }

    # Translation mapping for keys
    key_translation = {
        "_id": "id",
        "url": "url",
        "name": "name",
        "country": "country",
        "province": "province",
        "city": "city",
        "area": "area",
        "address": "address",
        "phone": "phone",
        "ساعت کار": "working_hours",
        "صبحانه": "breakfast",
        "فضای باز": "open_space",
        "سیگار کشیدن": "smoking",
        "موزیک": "music",
        "تلویزیون": "tv",
        "ویدیو پروژکتور": "projector",
        "فضای ویژه VIP": "vip_space",
        "بازی و سرگرمی": "entertainment",
        "سلف‌سرویس": "self_service",
        "محدودیت زمانی": "time_limit",
        "مترو": "subway",
        "بهترین‌های منو": "menu_bests",
        "Wi-Fi": "WiFi"
    }

    # Boolean normalization mapping
    yes_values = {"دارد", "بله", True, "True", "true"}
    no_values = {"ندارد", "خیر", "نه", False, "False", "false"}

    # Step 1: Remove unwanted keys
    for key in keys_to_remove:
        cafe.pop(key, None)

    # Step 2: Translate keys
    translated = {}
    for key, value in cafe.items():
        new_key = key_translation.get(key, key)
        translated[new_key] = value

    # Step 3: Normalize boolean values for selected keys
    bool_keys = {"breakfast", "open_space", "smoking", "music", "tv", "projector", "vip_space", "entertainment", "WiFi", "time_limit", "self_service"}

    for key in bool_keys:
        if key in translated:
            val = translated[key]
            if val in yes_values:
                translated[key] = "yes"
            else:
                translated[key] = "no"
        else:
            translated[key] = "no"

    # Step 4: Merge tv and projector into stream
    stream_val = "no"
    if translated.get("tv") == "yes" or translated.get("projector") == "yes":
        stream_val = "yes"
    translated["stream"] = stream_val
    translated.pop("tv", None)
    translated.pop("projector", None)

    # Step 5: Add index from URL
    url = translated.get("url", "")
    if "guide/" in url:
        translated["index"] = url.split("guide/")[-1]
    else:
        translated["index"] = ""

    return translated

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
        processed = process_cafe_data(cafe)

        if db[collection_name].find_one({"name": processed["name"]}):
            tqdm.write(f"[SKIPPED] {processed['name']} already exists")
            continue

        try:
            db[collection_name].insert_one(processed)
            tqdm.write(f"[SAVED] {processed['name']} → {collection_name}")
        except Exception as e:
            tqdm.write(f"[ERROR] Failed to insert {processed['name']}: {e}")
