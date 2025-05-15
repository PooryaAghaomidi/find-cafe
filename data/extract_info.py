import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


class ExtractInfo:
    def __init__(self):
        self.name_path = 'h1[itemprop="name"]'
        self.geography_path = 'ol.breadcrumb li span[itemprop="name"]'
        self.area_path = 'body > section > div > div > div > div > div > div:nth-of-type(1) > div > div > div > ul:nth-of-type(1) > li:nth-of-type(4) > a'
        self.soup = None

    def extract_name(self):
        tag = self.soup.select_one(self.name_path)
        return tag.get_text(strip=True) if tag else None

    def extract_geography(self):
        items = self.soup.select(self.geography_path)
        return (
            items[2].get_text(strip=True) if len(items) > 2 else None,
            items[3].get_text(strip=True) if len(items) > 3 else None,
            items[4].get_text(strip=True) if len(items) > 4 else None
        )

    def extract_area(self):
        tag = self.soup.select_one(self.area_path)
        return tag.get_text(strip=True) if tag else None

    def extract_location(self):
        address = None
        phone = None

        address_tag = self.soup.find("div", itemprop="streetAddress")
        if address_tag:
            address = address_tag.get_text(strip=True).replace('آدرس ۱', '').strip()

        phone_tag = self.soup.find("div", itemprop="telephone")
        if phone_tag:
            phone = phone_tag.get_text(strip=True).replace('تلفن', '').strip()

        return {"address": address, "phone": phone}

    def extract_attributes(self):
        info = {}
        container = self.soup.find("div", class_="itemAttribute")

        if container:
            for div in container.find_all("div", class_=lambda c: c and c.startswith("field-")):
                spans = div.find_all("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(strip=True)
                    value = spans[1].get_text(strip=True).replace(":", "").strip()
                    info[key] = value
                elif len(spans) == 1:
                    info[spans[0].get_text(strip=True)] = ""

        return info

    def scrape_cafe(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            tqdm.write(f"[ERROR] Failed to fetch {url}: {e}")
            return {}

        name = self.extract_name()
        country, province, city = self.extract_geography()
        area = self.extract_area()
        location_data = self.extract_location()
        attributes = self.extract_attributes()

        result = {
            "url": url,
            "name": name,
            "country": country,
            "province": province,
            "city": city,
            "area": area,
            "address": location_data.get("address"),
            "phone": location_data.get("phone"),
            "attributes": attributes
        }

        for key, value in result.items():
            if value in (None, "", {}):
                tqdm.write(f"[WARNING] Missing '{key}' for {url}")

        return result


if __name__ == "__main__":
    input_file = "cafe_links.json"
    output_file = "cafe_data.jsonl"

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            urls = json.load(f)
    except Exception as e:
        print(f"[FATAL] Could not read input file: {e}")
        exit(1)

    extractor = ExtractInfo()

    with open(output_file, "w", encoding="utf-8") as out_f:
        for url in tqdm(urls):
            cafe_data = extractor.scrape_cafe(url)
            if cafe_data:
                out_f.write(json.dumps(cafe_data, ensure_ascii=False) + "\n")
