import json
import jsonlines
from collections import Counter

data = []
with jsonlines.open('cafe_clean.jsonl') as reader:
    for obj in reader:
        data.append(obj)

countries = []
provinces = []
cities = []
areas = []
attributes_keys = []
attributes_values = {}

for entry in data:
    countries.append(entry['country'])
    provinces.append(entry['province'])
    cities.append(entry['city'])
    areas.append(entry['area'])

    attributes = entry.get('attributes', {})
    for key, value in attributes.items():
        attributes_keys.append(key)
        
        if key not in attributes_values:
            attributes_values[key] = []
        attributes_values[key].append(value)


country_counts = Counter(countries)
province_counts = Counter(provinces)
city_counts = Counter(cities)
area_counts = Counter(areas)

attribute_key_counts = Counter(attributes_keys)
attribute_value_counts = {key: Counter(values) for key, values in attributes_values.items()}

result = {
    "country_counts": dict(country_counts),
    "province_counts": dict(province_counts),
    "city_counts": dict(city_counts),
    "area_counts": dict(area_counts),
    "attribute_key_counts": dict(attribute_key_counts),
    "attribute_value_counts": attribute_value_counts
}

with open('cafe_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print("Results saved to 'cafe_analysis.json'")
