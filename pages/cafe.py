import streamlit as st

# Page config
st.set_page_config(page_title="Café Delight", layout="wide")

# Title
st.title("☕ Café Delight")

# Top section: Images (horizontal layout)
st.markdown("### Explore Our Ambience")

# You can use local images or URLs
image_urls = [
    "1.jpg",  # example URLs
    "2.jpg",
    "3.jpg"
]

cols = st.columns(len(image_urls))
for col, img_url in zip(cols, image_urls):
    col.image(img_url, use_container_width=True)

# Divider
st.markdown("---")

# Bottom section: Cafe info
st.markdown("### 📍 Our Information")

st.markdown("""
**Name:** Café Delight  
**Address:** 123 Brew Street, Beanville, NY 10001  
**Phone:** (123) 456-7890  
**Email:** hello@cafedelight.com  
**Hours:**  
- Monday–Friday: 7:00 AM – 8:00 PM  
- Saturday–Sunday: 8:00 AM – 10:00 PM
""")

# Optional: Map (if you want to include a location)
st.map({
    "lat": [40.7128],   # Example: New York City coordinates
    "lon": [-74.0060]
})
