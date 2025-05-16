import base64
import streamlit as st
from chatbot import CafeFinder

CITIES = ["اصفهان", "تهران (استان)", "خراسان رضوی", "هرمزگان", "کرمان", "مازندران", "البرز", "فارس", "اردبیل",
          "گیلان", "گلستان", "آذربایجان شرقی", "سمنان", "کرمانشاه", "خوزستان", "بوشهر", "استان قزوین", "آذربایجان غربی"
          "قم", "زنجان", "مرکزی", "همدان", "یزد", "خراسان جنوبی", "کهگیلویه و بویراحمد", "سیستان و بلوچستان"]

st.set_page_config(page_title="کافه یاب", page_icon="☕", layout="wide", initial_sidebar_state="collapsed")

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

with open("retail-light-people-shop-table.jpg", "rb") as image:
    encoded = base64.b64encode(image.read()).decode()
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    .stButton>button {
        background-color: #6495ED; /* a little darker blue */
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover,
    .stButton>button:focus {
        background-color: #4169E1;  /* your hover background */
        color: white;    /* force white text */
        outline: none;              /* remove default focus outline */
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Make the page container a flexbox centered vertically and horizontally */
    .appview-container {
        display: flex;
        justify-content: center; /* horizontal center */
        align-items: center;     /* vertical center */
        height: 100vh;           /* full viewport height */
        padding: 0;              /* remove default padding */
    }

    /* Make block-container content a transparent box with padding */
    .block-container {
        background-color: rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 2rem;
        max-width: 700px;        /* control width */
        width: 90vw;             /* responsive width */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
        .css-1lcbmhc {
            padding-left: 1rem;
        }
    </style>
"""

st.markdown(hide_sidebar_style, unsafe_allow_html=True)


# --- State Initialization ---
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "my_class" not in st.session_state:
    st.session_state.my_class = None
if "last_cafes" not in st.session_state:
    st.session_state.last_cafes = []

# --- UI Header ---
st.title("کافه یاب")
selected_city = st.selectbox("لطفا شهر خود را انتخاب کنید", CITIES, key="selected_city")

# --- Start Conversation ---
if st.button("شروع گشتن در این شهر"):
    st.session_state.my_class = CafeFinder(
        selected_city,
        "aa-cMenpBRK6Adc94FY7GOCGfWsL3ac5JNn7guKcWPxGw0WwmLg",
        "https://api.avalai.ir/v1",
        "gpt-4o"
    )
    st.session_state.chat_started = True
    st.session_state.messages = [{"role": "assistant", "content": "سلام 😀 برای پیدا کردن کافه چه ویژگی هایی تو ذهنته؟"}]
    st.session_state.chat_id = None
    st.session_state.last_cafes = []

    st.session_state.all_cafes = st.session_state.my_class.collection.find()

    st.switch_page("pages/finder.py")