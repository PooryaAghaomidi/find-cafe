import streamlit as st

st.markdown(
    """
    <style>
    /* Hide the Streamlit header (top menu bar) */
    header {visibility: hidden;}
    
    /* Hide the footer */
    footer {visibility: hidden;}
    
    /* Optional: to remove the extra blank space left behind */
    .css-18e3th9 {padding-top: 0rem;}
    </style>
    """,
    unsafe_allow_html=True
)

cafe = st.session_state.get("selected_cafe")
value_translation = {True: "بله", False: "خیر", "yes": "بله", "no": "نه"}
excluded_keys = {'country', 'province', 'city', 'url', '_id', 'index'}
label_mapping = {
    'name': 'نام',
    'country': 'کشور',
    'province': 'استان',
    'city': 'شهر',
    'area': 'محدوده',
    'address': 'آدرس',
    'phone': 'تلفن',
    'working_hours': 'ساعات کاری',
    'breakfast': 'صبحانه',
    'open_space': 'محیط باز',
    'smoking': 'سیگار',
    'music': 'موسیقی',
    'vip_space': 'فضای VIP',
    'entertainment': 'سرگرمی',
    'WiFi': 'وای‌فای',
    'self_service': 'سلف‌سرویس',
    'time_limit': 'محدودیت زمانی',
    'stream': 'پخش زنده',
    'menu_bests': 'بهترین های منو',
    'subway': 'مترو'
}

cleaned_cafe = {}
for key in cafe:
    value = cafe[key]
    if value is not None:
        cleaned_cafe[key] = value_translation.get(value, value)

st.title(f"☕ {cleaned_cafe['name']}")
st.markdown("### محیط ما را تجربه کنید")
image_urls = ["pages/1.jpg", "pages/2.jpg", "pages/3.jpg"]

cols = st.columns(len(image_urls))
for col, img_url in zip(cols, image_urls):
    col.image(img_url, use_container_width=True)

st.markdown("---")
st.markdown("### 📍 اطلاعات")

markdown_lines = ['<ul dir="rtl" style="text-align: right;">']
for key, value in cleaned_cafe.items():
    if key in excluded_keys:
        continue
    label = label_mapping.get(key, key)
    markdown_lines.append(f"<li><strong>{label}:</strong> {value}</li>")
markdown_lines.append('</ul>')

st.markdown('\n'.join(markdown_lines), unsafe_allow_html=True)

st.map({"lat": [35.7219], "lon": [51.3347]})
