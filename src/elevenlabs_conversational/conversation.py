import threading
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.conversational_ai.conversation import ClientTools

conversation = None
thread = None

def start_conversation_in_thread():
    global thread
    thread = threading.Thread(target=main)
    print(f"Starting conversation in thread: {thread.native_id} ")
    thread.start()

def stop_conversion_thread():
    global conversation 
    global thread
    if conversation and thread:
        print(f"Stopping conversation in thread: {thread.native_id}")
        conversation.end_session()

def main():
    global conversation

    load_dotenv()
    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    client_tools = ClientTools()

    def get_age():
        age = 22
        return age

    def log_message(parameters):
        message = parameters.get("message")
        print(f"message: {message}")

    def get_customer_details():
        customer_data = {
            "id": 123,
            "name": "Kobe",
            "Subscription": "None"
        }
        return customer_data

    client_tools.register("getAge", get_age)
    client_tools.register("logMessage", log_message)
    client_tools.register("getCustomerDetails", get_customer_details)

    conversation = Conversation(
        client=elevenlabs,
        agent_id=os.getenv("AGENT_ID"),
        requires_auth=True,
        audio_interface=DefaultAudioInterface(),
        client_tools=client_tools,
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        # callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    )

    conversation.start_session()

    conversation_id=conversation.wait_for_session_end()
    print(f"Conversation ID: {conversation_id}")
