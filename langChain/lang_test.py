import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-4", api_key=openai_api_key)

# Create a list of messages that will be sent to the AI model
# SystemMessage sets the context/behavior for the AI
# HumanMessage contains the actual user input
messages = [
    SystemMessage("Translate the following from English into Italian"),  # Instructions for the AI
    HumanMessage("hi!"),  # The text to be translated
]

response = model.invoke(messages)

print(response.content)
