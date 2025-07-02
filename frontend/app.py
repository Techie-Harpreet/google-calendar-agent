# frontend/app.py

import streamlit as st
import requests
import uuid

# --- Page Configuration ---
st.set_page_config(
    page_title="TailorTalk",
    page_icon="💬"
)

st.title("💬 TailorTalk Appointment Bot")
st.caption("Your friendly AI agent for booking appointments")


# --- Session State Initialization ---
# This is like the app's memory for each user session.
# We store the chat history and a unique session ID.

# The backend API URL
# When running locally, both are on your machine.
# When deployed, this will be the URL of your deployed backend.
# BACKEND_URL = "http://127.0.0.1:8000/chat" 
BACKEND_URL = "https://fastapi.harpreetsinghbansal.shop/chat" 


# Initialize session_id if it doesn't exist
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize chat history (messages) if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you book an appointment today?"}
    ]


# --- Chat Interface ---

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Get new user input
if prompt := st.chat_input("What would you like to do?"):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Prepare the data to send to the backend
    payload = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }
    
    # Show a thinking spinner while waiting for the backend
    with st.spinner("Thinking..."):
        try:
            # Send the message to the backend API
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()  # Raises an exception for bad status codes
            
            # Get the agent's response from the JSON
            agent_response = response.json().get("response")

            # Add agent's response to session state and display it
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            st.chat_message("assistant").write(agent_response)

        except requests.exceptions.RequestException as e:
            # Handle connection errors or other request issues
            error_message = f"Failed to connect to the backend: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
