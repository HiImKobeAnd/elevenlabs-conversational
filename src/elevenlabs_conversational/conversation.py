import threading
import time
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import AudioEventAlignment, Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.conversational_ai.conversation import ClientTools

conversation = None
thread = None

countdown_start_time = None
audio_end_ms = 0
cumulative_audio_ms = 0
countdown_lock = threading.Lock()


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


def countdown_display_loop():
    global countdown_start_time, audio_end_ms, cumulative_audio_ms
    while True:
        time.sleep(0.1)
        with countdown_lock:
            if countdown_start_time is None:
                continue
            elapsed_ms = (time.time() - countdown_start_time) * 1000
            remaining_ms = max(0, audio_end_ms - elapsed_ms)

        if remaining_ms > 0:
            print(f"Countdown: {remaining_ms / 1000:.1f}s remaining")
        else:
            with countdown_lock:
                if audio_end_ms > 0:
                    print(f"Countdown complete (total was {audio_end_ms:.0f}ms)")
                    countdown_start_time = None
                    audio_end_ms = 0
                    cumulative_audio_ms = 0


def audio_alignment_callback(audio_alignment: AudioEventAlignment):
    global countdown_start_time, audio_end_ms, cumulative_audio_ms

    with countdown_lock:
        if countdown_start_time is None:
            countdown_start_time = time.time()
            threading.Thread(target=countdown_display_loop, daemon=True).start()

        if audio_alignment.char_start_times_ms:
            chunk_end_ms = max(
                start + dur
                for start, dur in zip(
                    audio_alignment.char_start_times_ms,
                    audio_alignment.char_durations_ms,
                )
            )
            cumulative_audio_ms += chunk_end_ms
            audio_end_ms = cumulative_audio_ms


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
        customer_data = {"id": 123, "name": "Kobe", "Subscription": "None"}
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
        callback_latency_measurement=lambda latency: print(f"Latency: {latency}"),
        # callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
        callback_audio_alignment=lambda audio_alignment: audio_alignment_callback(
            audio_alignment
        ),
    )

    conversation.start_session()

    conversation_id = conversation.wait_for_session_end()
    print(f"Conversation ID: {conversation_id}")
