import pandas as pd
import streamlit as st
from chatbot import CafeFinder


CITIES = ["اصفهان",
    "تهران (استان)",
    "خراسان رضوی",
    "هرمزگان",
    "کرمان",
    "مازندران",
    "البرز",
    "فارس",
    "گیلان",
    "گلستان",
    "آذربایجان شرقی",
    "سمنان",
    "کرمانشاه",
    "خوزستان",
    "بوشهر",
    "استان قزوین",
    "قم",
    "زنجان",
    "مرکزی",
    "همدان",
    "یزد",
    "آذربایجان غربی",
    "خراسان جنوبی",
    "کهگیلویه و بویراحمد",
    "سیستان و بلوچستان",
    "اردبیل"]

if 'started' not in st.session_state:
    st.session_state.started = False
if 'city' not in st.session_state:
    st.session_state.city = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'cafe_results' not in st.session_state:
    st.session_state.cafe_results = []

def start_chat():
    st.session_state.my_class = CafeFinder(st.session_state.selected_city, 
                                           "aa-cMenpBRK6Adc94FY7GOCGfWsL3ac5JNn7guKcWPxGw0WwmLg", 
                                           "https://api.avalai.ir/v1", 
                                           "gpt-4o")

    if st.session_state.selected_city:
        st.session_state.city = st.session_state.selected_city
        st.session_state.started = True
        st.session_state.history = []
        st.rerun()

st.title("کافه یاب هوشمند")

if not st.session_state.started:
    st.write("لطفا شهر مورد نظرتون رو انتخاب کنید")
    st.selectbox("شهر را انتخاب کنید", CITIES, key="selected_city")
    st.button("شروع مکالمه", on_click=start_chat)
else:
    for speaker, msg in st.session_state.history:
        if speaker == 'user':
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

    user_input = st.chat_input("متن خود را بنویسید ...")
    if user_input:
        st.session_state.history.append(("user", user_input))
        
        answer = answer = st.session_state.my_class.find_cafe(user_input,
                                                              [],
                                                              {"name": None, "area": None, "smoke": None, "open_space": None, "game": None, "TV": None})

        items = [item["object"] for item in answer["items"]]
        cafe_data = []

        for item in items:
            open = "بله" if item.get('فضای باز') else "خیر"
            smoke = "بله" if item.get('سیگار کشیدن') else "خیر"
            game = "بله" if item.get('بازی و سرگرمی') else "خیر"
            tv = "بله" if item.get('تلویزیون') else "خیر"

            cafe_data.append({
                "نام": item.get('name', 'نامی موجود نیست'),
                "آدرس": item.get('address', 'اطلاعاتی موجود نیست'),
                "محیط باز": open,
                "آیا محیط سیگاری دارد؟": smoke,
                "وجود بازی؟": game,
                "تلویزیون؟": tv
            })

        st.session_state.cafe_results = cafe_data

        st.session_state.history.append(("assistant", answer["llm_response"]))
        st.rerun()

    if st.session_state.cafe_results:
        st.subheader("کافه‌های پیشنهادی:")
        df = pd.DataFrame(st.session_state.cafe_results)
        st.table(df)