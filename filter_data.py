import json
import jsonlines


def create_valids(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def filter_province(input_dict):
        return {k: v for k, v in input_dict.items() if v != 1 and k != "null"}

    valid_province = list(filter_province(data["province_counts"]).keys())
    valid_city = list(filter_province(data["city_counts"]).keys())
    return valid_province, valid_city


def apply_filter(json_file, valid_province, valid_city, remove_attributes, valid_attributes):
    cleaned_data = []

    with jsonlines.open(json_file) as reader:
        for entry in reader:
            if entry['country'] != 'ایران':
                continue
            
            if entry['province'] not in valid_province:
                continue
            else:
                if entry['city'] not in valid_city:
                    entry['city'] = None
            
            if entry['area'] == "":
                entry['area'] = None
            
            attributes = entry.get('attributes', {})
            for key, value in attributes.items():
                if key not in remove_attributes:
                    if key in valid_attributes:
                        if value in valid_attributes[key]:
                            entry[key] = valid_attributes[key][value]
                        else:
                            entry[key] = None
                    else:
                        entry[key] = value

            if 'attributes' in entry:
                del entry['attributes']
            cleaned_data.append(entry)

    return cleaned_data


if __name__ == "__main__":
    valid_attributes = {
        "فضای باز": {
            "دارد": True,
            "ندارد": False
        },
        "سیگار کشیدن": {
            "آزاد است": True,
            "فقط در قسمت فضای باز": True,
            "فضای مخصوص دارد": True,
            "آزاد نیست": False,
            "عصر به بعد": True
        },
        "تلویزیون": {
            "دارد": True,
            "ندارد": False
        },
        "بازی و سرگرمی": {
            "دارد": True,
            "ندارد": False
        },
        "سلف‌سرویس": {
            "دارد": True,
            "ندارد": False
        },
        "Wi-Fi": {
            "دارد": True,
            "ندارد": False
        }
    }

    remove_attributes = [
        "اینستاگرام",
        "فروشگاه",
        "دستگاه کارت‌خوان",
        "قهوه موج سوم",
        "سرویس بهداشتی",
        "پریز برق",
        "مناسب برای معلولین",
        "ظرفیت",
        "گالری",
        "اتوبوس",
        "تاکسی",
        "فیس‌بوک",
        "تلگرام",
        "کانال تلگرام",
        "توییتر",
        "صفحه لینک این"
    ]

    valid_province, valid_city = create_valids('cafe_analysis.json')
    cleaned_data = apply_filter('cafe_clean.jsonl', valid_province, valid_city, remove_attributes, valid_attributes)
    
    with jsonlines.open('cafe_ready.jsonl', 'w') as writer:
        for entry in cleaned_data:
            writer.write(entry)

    print("Data cleaning completed and saved as cafe_ready.json")
