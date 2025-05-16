# Use official Python 3.9 image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Run database init and then launch Streamlit
CMD ["bash", "-c", "python create_database.py && streamlit run home.py --server.port=8501 --server.enableCORS=false --server.headless=true"]
