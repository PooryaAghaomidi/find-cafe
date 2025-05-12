import json
import re
from tqdm import tqdm
from urllib.parse import unquote

def is_persian_url(url):
    decoded = unquote(url)
    return bool(re.search(r'[\u0600-\u06FF]', decoded))

def is_valid_cafe(cafe):
    return (
        cafe.get("name") is not None and
        cafe.get("location") is not None and
        cafe.get("attributes")
    )

if __name__ == "__main__":
    input_file = "cafe_data.jsonl"
    output_file = "cafe_clean.jsonl"

    filtered_cafes = []

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

        filtered_cafes.append(cafe)

    with open(output_file, "w", encoding="utf-8") as out_file:
        for cafe in filtered_cafes:
            out_file.write(json.dumps(cafe, ensure_ascii=False) + "\n")

    tqdm.write(f"Filtered cafes have been saved to {output_file}")
