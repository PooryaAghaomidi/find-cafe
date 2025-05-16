import os
import re
import json
import uuid
import logging
from openai import OpenAI
from pymongo import MongoClient


class CafeFinder:
    def __init__(self, province, api_key, base_url, llm_model="gpt-4o"):
        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        client = MongoClient(MONGO_URI)
        self.collection = client["places"][province]
        self.chats = client["places"]["chats"]

        self.llm_model = llm_model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        logging.basicConfig(level=logging.INFO)

        self.main_system_prompt = """
                                  تو یک دستیار هوشمند هستی که به افراد کمک می‌کند تا کافه یا رستوران مورد نظرشان را پیدا کنند.
                                  من به تو میگویم که وضعیت پیدا شدن یا نشدن کافه مورد نظر چیست و تو به کاربر نتیجه را اطلاع بده
                                  """


    def extraction_agent(self, text):
        prompt = f"""
                  You are a helpful assistant. You extract information related to cafe or restaurant features.
                  Here are the features you must extract from a Persian text you get:
                  1. name: Name of the place (نام کافه یا رستوران)
                  2. area: Location or area of the place  (محله یا آدرس کافه یا رستوران)
                  3. subway: Nearest subway station name  (نزدیکی کافه یا رستوران به کدام ایستگاه مترو)
                  4. smoking: If you can smoke  (امکان سیگار کشیدن در کافه یا رستوران)
                  5. entertainment: If you can play game (امکان بازی و سرگرمی در کافه یا رستوران)
                  6. stream: If you can watch TV stream  (امکان تماشای تلویزیون یا داشتن ویدئو پروژکتور برای دیدن فوتبال)
                  7. open_space: If it has an open space  (فضای باز بدون سقف یا روف گاردن)
                  8. breakfast: If they serve breakfast  (داشتن صبحانه در منو)
                  9. music: If they play music  (پخش موسیقی در کافه یا رستوران)
                  10. vip_space: If they have VIP space  (داشتن فضای ویژه یا اختصاصی در کافه یا رستوران)
                  11. WiFi: If they have Wi-Fi  (داشتن اینترنت در کافه یا رستوران)
                  12. time_limit: If they have time limit  (محدودیت زمانی برای نشستن در کافه یا رستوران)

                  Message:
                  {text}

                  If any variable is missing in the message, it must be null.
                  Your output must be a structures JSON file like this:

                  {{
                      "name": "...",
                      "area": "...",
                      "subway": "...",
                      "smoking": "yes or no",
                      "open_space": "yes or no",
                      "breakfast": "yes or no",
                      "music": "yes or no",
                      "vip_space": "yes or no",
                      "entertainment": "yes or no",
                      "WiFi": "yes or no",
                      "time_limit": "yes or no",
                      "stream": "yes or no"
                  }}

                  Output only the JSON structure. Do not add any explanation or commentary.
                  """

        resp = self.client.chat.completions.create(model=self.llm_model,
                                            messages=[{"role": "user", "content": prompt}])
        content = resp.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.DOTALL)

        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return {"name": None,
                    "area": None,
                    "subway": None,
                    "smoking": None,
                    "open_space": None,
                    "breakfast": None,
                    "music": None,
                    "vip_space": None,
                    "entertainment": None,
                    "WiFi": None,
                    "time_limit": None,
                    "stream": None}

        required_keys = ["name", "area", "subway", "smoking", "open_space", "breakfast",
                         "music", "vip_space", "entertainment", "WiFi", "time_limit", "stream"]
        boolean_keys = ["smoking", "open_space", "breakfast", "music", "vip_space", "entertainment",
                        "WiFi", "time_limit", "stream"]

        for key in required_keys:
            if key not in content:
                content[key] = None

        for key in boolean_keys:
            value = content.get(key)
            if isinstance(value, str):
                if value.lower() == "yes":
                    content[key] = True
                elif value.lower() == "no":
                    content[key] = False
            else:
                content[key] = None

        return content


    def _calculate_points(self, document, criteria):
        points = 0
        
        for key in ["smoking", "open_space", "breakfast", "music", "vip_space", 
                    "entertainment", "WiFi", "time_limit", "stream"]:
            if key in criteria and key in list(document.keys()):
                if document.get(key) == criteria[key]:
                    points += 1

        if 'name' in criteria and criteria['name'] is not None and criteria['name'] in document.get('name', ''):
            points += 1

        if 'subway' in criteria and criteria['subway'] is not None and criteria['subway'] in document.get('subway', ''):
            points += 1

        if 'area' in criteria:
            if criteria['area'] in document.get('area', ''):
                points += 1
            elif criteria['area'] in document.get('address', ''):
                points += 1
        return points
    

    def _process_doc(self, document):
        required_keys = ["name", "area", "subway", "smoking", "open_space", "breakfast",
                         "music", "vip_space", "entertainment", "WiFi", "time_limit", "stream"]
        boolean_keys = ["smoking", "open_space", "breakfast", "music", "vip_space", "entertainment",
                        "WiFi", "time_limit", "stream"]

        for key in required_keys:
            if key not in document:
                document[key] = None

        for key in boolean_keys:
            value = document.get(key)
            if isinstance(value, str):
                if value.lower() == "yes":
                    document[key] = True
                elif value.lower() == "no":
                    document[key] = False
            else:
                document[key] = None
        
        return document
    

    def _retrieve_objects(self, criteria):
        cursor = self.collection.find()
        result = []

        max_point = 0
        for document in cursor:
            document = self._process_doc(document)
            points = self._calculate_points(document, criteria)
            if points > 0:
                result.append({'object': document, 'point': points})

                if points > max_point:
                    max_point = points

        result_sorted = sorted(result, key=lambda x: x['point'], reverse=True)
        return result_sorted, max_point
    

    def _llm_agent(self, chat_id, chat_data, system_prompt, status, items):
        chat_data = self._update_id(chat_id=chat_id, system_prompt=system_prompt, status=status, items=items)
        resp = self.client.chat.completions.create(model=self.llm_model, messages=chat_data["history"], temperature=0.1)
        llm_response = resp.choices[0].message.content.strip()

        self.chats.update_one(
            {"chat_id": chat_id},
            {
                "$push": {
                    "history": {"role": "assistant", "content": llm_response}
                }
            }
        )

        chat_data = self.chats.find_one({"chat_id": chat_id})
        return chat_data
    

    def _create_id(self, query):
        chat_id = str(uuid.uuid4())

        history = [
            {"role": "system", "content": self.main_system_prompt},
            {"role": "user", "content": f"پیام کاربر: {query}"}
        ]

        latest_criteria = {"name": None,
                           "area": None,
                           "subway": None,
                           "smoking": None,
                           "open_space": None,
                           "breakfast": None,
                           "music": None,
                           "vip_space": None,
                           "entertainment": None,
                           "WiFi": None,
                           "time_limit": None,
                           "stream": None}
        
        self.chats.insert_one({
            "chat_id": chat_id,
            "history": history,
            "latest_criteria": latest_criteria
        })
        return chat_id, latest_criteria
    

    def _retrieve_id(self, chat_id, query):
        self.chats.update_one(
            {"chat_id": chat_id},
            {
                "$push": {
                    "history": {"role": "user", "content": f"پیام کاربر: {query}"}
                }
            }
        )
        
        chat_data = self.chats.find_one({"chat_id": chat_id})
        return chat_data["latest_criteria"]
    

    def _update_id(self, chat_id, system_prompt, status, items):
        self.chats.update_one(
            {"chat_id": chat_id},
            {
                "$push": {
                    "history": {"role": "assistant", "content": f"وضعیت پیدا کردن کافه یا رستوران مورد نظر: {system_prompt}"}
                },
                "$set": {
                    "status": status,
                    "items": items
                }
            }
        )

        chat_data = self.chats.find_one({"chat_id": chat_id})
        return chat_data
    

    def _update_criteria(self, chat_id, latest_criteria):
        self.chats.update_one({"chat_id": chat_id},
                              {"$set": {"latest_criteria": latest_criteria}})


    def find_cafe(self, query, chat_id=None):
        if chat_id is None:
            chat_id, latest_criteria = self._create_id(query)
            logging.info(f"Chat created with this ID: {chat_id}")
        else:
            latest_criteria = self._retrieve_id(chat_id, query)
            logging.info(f"Chat retrieved with this ID: {chat_id}")

        new_criteria = self.extraction_agent(query)
        logging.info(f"Extracted information: {new_criteria}")

        for key in latest_criteria:
            if new_criteria[key] is not None:
                latest_criteria[key] = new_criteria[key]
        self._update_criteria(chat_id, latest_criteria)
        logging.info(f"Updated information: {latest_criteria}")

        required_point = sum(1 for value in latest_criteria.values() if value is not None)
        logging.info(f"Number of required criteria: {required_point}")

        if required_point == 0:
            system_prompt="برای این پیام کاربر موردی برای نشان دادن پیدا نشد"
            status="no valid filter"
            result_sorted = []
            chat_data = self.chats.find_one({"chat_id": chat_id})
        else:
            result_sorted, max_point = self._retrieve_objects(latest_criteria)
            chat_data = self.chats.find_one({"chat_id": chat_id})
            logging.info(f"Number of retrieved items: {len(result_sorted)}")
            logging.info(f"With the maximum point: {max_point}")

            result_sorted[:] = [item for item in result_sorted if item['point'] == max_point]
            logging.info(f"Number of retrieved items after filtering: {len(result_sorted)}")

            if not result_sorted:
                system_prompt = """
                                برای این پیام کاربر موردی برای نشان دادن پیدا نشد
                                به او بگو که با مشخصات دیگری دوباره تلاش کند
                                """
                status="not found"
            elif max_point < required_point:
                system_prompt = f"""
                                برای این پیام کاربر
                                {len(result_sorted)}
                                مورد پیدا شد ولی دقیقا مطابق خواسته های او نیست
                                به او بگو که میتواند موارد پیدا شده را در قسمت نتایج ببیند
                                """
                status="incomplete"
            else:
                system_prompt = f"""
                                محل مورد نظر پیدا شد
                                به او بگو که میتواند موارد پیدا شده را در قسمت نتایج ببیند
                                """
                status="complete"
        
        chat_data = self._llm_agent(chat_id=chat_id, chat_data=chat_data, system_prompt=system_prompt, status=status, items=result_sorted)
        logging.info(f"Conversation finished")
        return chat_data
