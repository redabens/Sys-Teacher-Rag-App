fastapi: uvicorn logic:app --host 0.0.0.0 --port 8000 --reload 2>&1 | tee /app/logs/fastapi.log
streamlit: streamlit run chatPage.py --server.port 8501 --server.address 0.0.0.0 2>&1 | tee /app/logs/streamlit.log
