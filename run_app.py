import threading
import uvicorn
from backend.main import app  # your FastAPI app
from streamlit.web.bootstrap import run
from streamlit.web.server import Server

def run_streamlit():
    Server._singleton = None  # Prevent Streamlit from crashing on reload

    run(
        "frontend/app.py",
        args=[],
        flag_options={
            "server.port": 10001,
            "server.address": "0.0.0.0"
        },
        is_hello=False
    )

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_streamlit).start()
    run_fastapi()
