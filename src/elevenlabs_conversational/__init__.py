from fastapi import FastAPI
from elevenlabs_conversational.conversation import (
    start_conversation_in_thread,
    stop_conversation_thread,
)

app = FastAPI()


@app.get("/start")
async def start():
    thread = start_conversation_in_thread()
    return {"status": "started", "thread_id": thread.native_id}


@app.get("/stop")
async def stop():
    stop_conversation_thread()
    return {"status": "stopped"}
