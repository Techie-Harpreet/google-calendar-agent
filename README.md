# Google Calendar AI Agent 🤖

This project is a conversational AI agent designed to help users book appointments directly on their Google Calendar through a simple chat interface. Powered by Google's Gemini model and built with Langchain, this agent can understand natural language, check for calendar availability, and confirm bookings in real-time.

---

## 🚀 Live Demo

**You can try the live application here:** **[calendar-agent-ai.streamlit.app](https://calendar-agent-ai.streamlit.app/)**

![Screenshot](https://i.imgur.com/r6hS0hO.png)

---

## ✨ Features

- **Natural Conversation:** Engage in a natural, back-and-forth conversation to schedule appointments.
- **Calendar Availability:** Automatically checks your Google Calendar to see if a time slot is free before booking.
- **Appointment Booking:** Seamlessly creates events in your calendar with a specified title and time.
- **Function Calling:** Uses Langchain's agent framework to intelligently decide when to use its tools.

---

## 💬 Example Prompts

Here are a few examples of how you can interact with the agent:

- **Check for availability:**
  > "Are you free tomorrow at 4 PM?"

- **Book an appointment directly:**
  > "Book a meeting for 'Project Discussion' on Friday at 11 AM."

- **Have a multi-step conversation:**
  > **You:** "Check if I'm busy on July 15th at 3 PM."
  > **Agent:** "That time is free."
  > **You:** "Great, please book 'Team Sync' for that time."

---

## 🛠️ Tech Stack

- **Backend:** **Python** with **FastAPI**
- **Frontend:** **Streamlit**
- **AI Framework:** **Langchain**
- **LLM Model:** **Google Gemini**
- **API Integration:** **Google Calendar API**

---

## ⚙️ Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.9+
- A Google Cloud account

### 1. Google Calendar API Setup

Before running the application, you need to configure access to the Google Calendar API.

1.  **Create a Google Cloud Project:** Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  **Enable the Google Calendar API:** In your project, search for and enable the "Google Calendar API".
3.  **Create a Service Account:** Navigate to "Service Accounts" and create a new service account. Grant it the "Owner" role for simplicity.
4.  **Generate a JSON Key:** Create a key for the service account (in JSON format). This will download a `credentials.json` file. Place this file in the root directory of this project.
5.  **Share Your Calendar:**
    - Find the `client_email` inside your `credentials.json` file.
    - Go to your Google Calendar's "Settings and sharing" menu.
    - Under "Share with specific people or groups," add the `client_email` and give it permission to **"Make changes to events"**.

### 2. Clone & Install

Clone the repository and install the required Python packages.

```bash
# Clone the repository
git clone [https://github.com/Techie-Harpreet/google-calendar-agent.git](https://github.com/Techie-Harpreet/google-calendar-agent.git)
cd google-calendar-agent

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a file named `.env` in the root of the project directory. This file will hold your secret keys.

1.  Get your **Calendar ID** from your Google Calendar's settings page (under the "Integrate calendar" section).
2.  Get your **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
3.  Add these keys to the `.env` file:

```
# .env file

CALENDAR_ID="your_google_calendar_id@group.calendar.google.com"
GEMINI_API_KEY="your_gemini_api_key_here"
```

---

## 💻 Usage

You need to run the backend and frontend servers in two separate terminals.

**Terminal 1: Run the Backend**

```bash
uvicorn backend.main:app --reload
```
This will start the FastAPI server at `http://1227.0.0.1:8000`.

**Terminal 2: Run the Frontend**

```bash
streamlit run frontend/app.py
```
This will open the Streamlit chat interface in your browser.

---

## ☁️ Deployment

This application was deployed on [Render](https://render.com/) and [Streamlit Community Cloud](https://streamlit.io/cloud).

- **Backend Service:** Deployed on Render as a Web Service. Environment variables and the `credentials.json` secret file were configured on the platform.
- **Frontend Service:** Deployed on Streamlit Community Cloud, with the `BACKEND_URL` environment variable pointing to the public URL of the deployed backend service.
