# Import the os module to access environment variables and system functions
import os

# Import load_dotenv function to load environment variables from a .env file
from dotenv import load_dotenv

# Import ChatOpenAI class which provides interface to OpenAI's chat models
from langchain_openai import ChatOpenAI

# Import message classes for structured communication with the AI model
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables from .env file into the current environment
# This makes variables like OPENAI_API_KEY available via os.getenv()
load_dotenv()

# Retrieve the OpenAI API key from environment variables
# This is a secure way to access sensitive credentials without hardcoding them
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create an instance of ChatOpenAI model configured to use GPT-4
# The api_key parameter ensures the model uses our specific API key
model = ChatOpenAI(model="gpt-4", api_key=openai_api_key)

# Create a list of messages that will be sent to the AI model
# SystemMessage sets the context/behavior for the AI
# HumanMessage contains the actual user input
messages = [
    SystemMessage("Translate the following from English into Italian"),  # Instructions for the AI
    HumanMessage("hi!"),  # The text to be translated
]

# Send the messages to the AI model and get the response
# invoke() method processes the conversation and returns the AI's reply
response = model.invoke(messages)

# Print the content of the AI's response to the console
# response.content contains the translated text "ciao!"
print(response.content)
