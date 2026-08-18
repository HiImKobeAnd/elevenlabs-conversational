from fastapi import FastAPI
from elevenlabs_conversational.conversation import (
    start_conversation_in_thread,
    stop_conversion_thread,
)

app = FastAPI()


@app.get("/start")
async def start():
    thread = start_conversation_in_thread()
    print(thread)


@app.get("/stop")
async def stop():
    stop_conversion_thread()
