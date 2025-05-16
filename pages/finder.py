import pandas as pd
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
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_cafes" not in st.session_state:
    st.session_state.last_cafes = []

def on_card_click(cafe):
    st.session_state.selected_cafe = cafe
    st.toast(f"Clicked on {cafe.get('name', 'Cafe')}")
    st.switch_page("pages/cafe.py")

# --- Split into two columns ---
col1, col2 = st.columns([2, 2])
user_input = st.chat_input("مثلا یک کافه اطراف سعادت آباد خواستم که فضای باز داشته باشه")

with col1:
    # --- Chat Interface ---
    if st.session_state.chat_started:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})

            response = st.session_state.my_class.find_cafe(user_input, st.session_state.chat_id)
            st.session_state.chat_id = response["chat_id"]

            assistant_response = response["history"][-1]["content"]
            st.chat_message("assistant").markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            # Extract cafes and store for later rendering
            cafes = [item["object"] for item in response.get("items", [])]
            st.session_state.last_cafes = cafes
            st.session_state.show_results_button = True

    if st.session_state.get("last_cafes"):
        with col2:
            cafes = st.session_state.last_cafes
            num_cols = 5
            rows = [cafes[i:i + num_cols] for i in range(0, len(cafes), num_cols)]

            for row in rows:
                cols = st.columns(len(row), gap="small")
                for cafe, col in zip(row, cols):
                    with col:
                        card_container = st.container()
                        with card_container:
                            st.image("pages/1.jpg", width=150)

                            button_label = cafe.get("name", "Cafe")

                            if st.button(button_label, key=f"btn_{button_label}"):
                                on_card_click(cafe)