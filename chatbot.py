import re
import json
from openai import OpenAI
from pymongo import MongoClient


class CafeFinder:
    def __init__(self, province, api_key, base_url, llm_model="gpt-4o"):
        client = MongoClient("mongodb://localhost:27017/")
        self.collection = client["places"][province]

        self.llm_model = llm_model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def extraction_agent(self, text):
        prompt = f"""
                  تو یک استخراج کننده اطلاعات از متن هستی که باید اطلاعات مورد نظر زیر رو از پیام استخراج کنی:
                  1. نام کافه یا رستوران
                  2. موقعیت مکانی/محل رستوران
                  3. قابلیت سیگار کشیدن در محل
                  4. فضای باز
                  5. بازی و سرگرمی
                  6. تلویزیون

                  اگر هر کدام از اطلاعات بالا ذکر نشده بود مقدار null انتخاب کن

                  متن:
                  {text}

                  جواب باید یک فایل JSON به شکل زیر باشد
                  {{
                      "name": "...",
                      "area": "...",
                      "smoke": True or False,
                      "open_space": True or False,
                      "game": True or False,
                      "TV": True or False
                  }}
                  """

        resp = self.client.chat.completions.create(model=self.llm_model,
                                            messages=[{"role": "user", "content": prompt}])
        content = resp.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.DOTALL)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"name": None, "area": None, "smoke": None, "open_space": None, "game": None, "TV": None}

    def _calculate_points(self, document, criteria):
        points = 0
        
        for key in ['سیگار کشیدن', 'فضای باز', 'بازی و سرگرمی', 'تلویزیون']:
            if key in criteria and document.get(key) == criteria[key]:
                points += 1

        if 'name' in criteria and criteria['name'] is not None and criteria['name'] in document.get('name', ''):
            points += 1

        if 'area' in criteria:
            if criteria['area'] in document.get('area', ''):
                points += 1
            elif criteria['area'] in document.get('address', ''):
                points += 1
        
        return points
    
    def _retieve_objects(self, criteria):
        cursor = self.collection.find()
        result = []

        max_point = 0
        for document in cursor:
            points = self._calculate_points(document, criteria)
            if points > 0:
                result.append({'object': document, 'point': points})

                if points > max_point:
                    max_point = points

        result_sorted = sorted(result, key=lambda x: x['point'], reverse=True)

        return result_sorted, max_point
    
    def llm_agent(self, query, system_prompt, messages):
        if messages == []:
            messages=[
                {"role": "system", "content": "تو یک دستیار هوشمند هستی که به افراد کمک می‌کند تا کافه یا رستوران مورد نظرشان را پیدا کنند."},
                {"role": "user", "content": f"پیام کاربر: {query}"},
                {"role": "assistant", "content": f"وضعیت پیدا کردن کافه یا رستوران مورد نظر: {system_prompt}"}
            ]
        else:
            messages.append(
                {"role": "user", "content": f"پیام کاربر: {query}"},
                {"role": "assistant", "content": f"وضعیت پیدا کردن کافه یا رستوران مورد نظر: {system_prompt}"}
            )

        resp = self.client.chat.completions.create(model=self.llm_model, messages=messages)
        llm_response = resp.choices[0].message.content.strip()

        messages.append({"role": "assistant", "content": llm_response})

        return llm_response, messages

    def find_cafe(self, query, former_messages, former_criteria):
        criteria = self.extraction_agent(query)

        mapping = {
            'smoke': 'سیگار کشیدن',
            'open_space': 'فضای باز',
            'game': 'بازی و سرگرمی',
            'TV': 'تلویزیون'
        }

        for key, new_value in mapping.items():
            if key in criteria:
                criteria[key] = new_value

        for key in former_criteria:
            if criteria[key] is not None:
                former_criteria[key] = criteria[key]

        required_point = sum(1 for value in former_criteria.values() if value is not None)

        if required_point == 0:
            system_prompt = "برای این پیام کاربر موردی برای نشان دادن پیدا نشد"
            status = "no valid filter"

            llm_response, messages = self.llm_agent(query, system_prompt, former_messages)

            return {
                "status": status,
                "llm_response": llm_response,
                "items": [],
                "criteria": former_criteria,
                "messages": messages
            }

        result_sorted, max_point = self._retieve_objects(former_criteria)
        
        if not result_sorted:
            system_prompt = """
            برای این پیام کاربر موردی برای نشان دادن پیدا نشد
            به او بگو که با مشخصات دیگری دوباره تلاش کند
            """
            status = "not found"
        elif max_point < required_point:
            system_prompt = f"""
            برای این پیام کاربر
            {len(result_sorted)}
            مورد پیدا شد ولی دقیقا مطابق خواسته های او نیست
            به او بگو که میتواند موارد پیدا شده را در سمت چپ تصویر ببیند
            """
            status = "incomplete"
        else:
            system_prompt = f"""
            محل مورد نظر پیدا شد
            به او بگو که میتواند موارد پیدا شده را در سمت چپ تصویر ببیند
            """
            status = "complete"

        llm_response, messages = self.llm_agent(query, system_prompt, former_messages)

        return {
            "status": status,
            "llm_response": llm_response,
            "items": result_sorted,
            "criteria": former_criteria,
            "messages": messages
        }


if __name__ == "__main__":
    my_class = CafeFinder("تهران (استان)", "aa-cMenpBRK6Adc94FY7GOCGfWsL3ac5JNn7guKcWPxGw0WwmLg", "https://api.avalai.ir/v1", "gpt-4o")

    answer = my_class.find_cafe("من یه کافه با فضای باز میخواستم اطراف خیبون شریعتی که بشه توش سیگار کشید.",
                                [],
                                {"name": None, "area": None, "smoke": None, "open_space": None, "game": None, "TV": None})

    print(answer)
