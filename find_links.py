import json
import requests
from bs4 import BeautifulSoup

sitemap_url = "https://www.cafeyab.com/sitemap.xml"
response = requests.get(sitemap_url)
soup = BeautifulSoup(response.content, "xml")

output_file = "cafe_links.json"
guide_links = []

for url_tag in soup.find_all("url"):
    loc = url_tag.find("loc")
    priority = url_tag.find("priority")

    if loc and priority:
        url_text = loc.text.strip()
        priority_text = priority.text.strip()

        if "/guide/" in url_text and priority_text == "0.8":
            guide_links.append(url_text)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(guide_links, f, ensure_ascii=False, indent=2)

print(f"Saved {len(guide_links)} cafe guide links with priority 0.8 to {output_file}")