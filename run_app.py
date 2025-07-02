import threading
import uvicorn
import streamlit.web.bootstrap as bootstrap
from backend.main import app  # FastAPI app from backend/

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=10000)

def run_streamlit():
    bootstrap.run('frontend/app.py', [])

if __name__ == "__main__":
    threading.Thread(target=run_streamlit).start()
    run_fastapi()
