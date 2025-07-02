import os
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel, Field

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- Langchain Imports ---
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage


# --- Setup and Configuration ---

# Load environment variables from .env file
load_dotenv()

# FastAPI app initialization
app = FastAPI(
    title="TailorTalk Agent API",
    description="API for the conversational AI agent to book appointments.",
    version="1.0.0",
)

# --- Google Calendar and LLM Setup ---
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
CALENDAR_ID = os.getenv('CALENDAR_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)


# --- Pydantic Schema for Tool Input ---
class BookAppointmentSchema(BaseModel):
    time: str = Field(description="The start time for the event in ISO 8601 format.")
    summary: str = Field(description="The title or summary of the event.")


# --- Google Calendar Tool Functions ---

def check_calendar_availability(time_str: str) -> str:
    """
    Checks the Google Calendar for events at a specified time to see if it's free.
    The input must be a single string in ISO 8601 format.
    """
    try:
        time_str = time_str.strip()
        start_dt = datetime.fromisoformat(time_str)
        end_dt = start_dt + timedelta(hours=1)
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID, timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(), singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            return f"The 1-hour slot starting at {start_dt.strftime('%I:%M %p')} is free."
        else:
            event_list = [f"'{event['summary']}'" for event in events]
            return f"The requested time slot is busy. It conflicts with: {', '.join(event_list)}."
    except Exception as e:
        return f"An error occurred: {e}"

def book_appointment(input_str: str) -> str:
    """
    Books a 1-hour appointment on Google Calendar.
    The input must be a JSON-like string containing a 'time' in ISO 8601 format and a 'summary'.
    """
    try:
        # The AI will send a string that looks like a dictionary.
        # We parse it into a real dictionary.
        args = json.loads(input_str.replace("'", '"'))

        time_str = args['time'].strip()
        summary = args['summary'].strip()

        start_dt = datetime.fromisoformat(time_str)
        end_dt = start_dt + timedelta(hours=1)
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_dt.isoformat()},
            'end': {'dateTime': end_dt.isoformat()},
        }
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        
        return f"Success! The appointment '{summary}' has been booked for {start_dt.strftime('%A, %B %d at %I:%M %p')}. Event link: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"An error occurred while booking: {e}"

# --- Langchain Agent Setup ---

# 1. Define the tools
tools = [
    Tool(
        name="CheckCalendarAvailability",
        func=check_calendar_availability,
        description="Use this to check if a specific time slot is available in the calendar. The input must be a single string representing the date and time in ISO 8601 format."
    ),
    # REPLACE the BookAppointment tool with this simple version
    Tool(
        name="BookAppointment",
        func=book_appointment,
        description="Use this to book a new 1-hour appointment in the calendar. The input must be a JSON-like string containing a 'time' key with the time in ISO 8601 format, and a 'summary' key with the appointment title."
    ),
]

# 2. Create the Prompt Template
prompt_template = """
You are a friendly and helpful AI assistant named TailorTalk. Your goal is to help users book appointments in their Google Calendar.

You have access to the following tools:
{tools}

To use a tool, please use the following format:
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action


When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
Thought: Do I need to use a tool? No
Final Answer: [your response here]


IMPORTANT:
- Today's date is {today}.
- Always be conversational and ask for clarification if the user's request is ambiguous.
- Before booking, always confirm the availability first unless the user explicitly asks to book without checking.
- The user's timezone is likely India Standard Time (IST, UTC+5:30). When you need to generate a time string for the tools, assume it's for today or a future date and include the timezone offset. For example: `{example_iso_time}`.

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""

today = datetime.now().strftime('%Y-%m-%d')
example_iso_time = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()

prompt = PromptTemplate.from_template(prompt_template)
prompt = prompt.partial(
    today=today,
    example_iso_time=example_iso_time,
)

# 3. Create the agent
agent = create_react_agent(llm, tools, prompt)

# 4. Create the Agent Executor
chat_histories = {}
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# --- FastAPI Endpoints ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """Handles the main chat interaction with the Langchain agent."""
    session_id = request.session_id
    
    if session_id not in chat_histories:
        chat_histories[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    memory = chat_histories[session_id]
    
    response = agent_executor.invoke({
        "input": request.message,
        "chat_history": memory.chat_memory.messages
    })
    
    memory.chat_memory.add_user_message(request.message)
    memory.chat_memory.add_ai_message(response['output'])
    
    return {"response": response['output']}


@app.get("/")
def read_root():
    return {"message": "Welcome to the TailorTalk Agent API!"}