# server.py
import io
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from starlette.responses import Response
from google import genai
from google.genai import types
import os

app = FastAPI()

@app.get("/ping")
def ping(): 
    return {"ok": True}

# ---- 환경 설정 ----
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY가 비어있습니다. .env나 환경변수를 설정하세요.")

MODEL = "gemini-live-2.5-flash-preview"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요한 도메인만 허용하도록 조정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=API_KEY)

async def async_enumerate(aiter):
    i = 0
    async for item in aiter:
        yield i, item
        i += 1

@app.post("/api/voice-reply")
async def voice_reply(payload: dict = Body(...)):
    """
    입력: {"text": "Hello?"}
    출력: audio/wav 바이트 (메모리, 파일 저장 X)
    """
    user_text = (payload.get("text") or "").strip()
    if not user_text:
        return Response(status_code=400, content="empty text")

    # Live 세션 연결 (AUDIO 응답)
    config = {"response_modalities": ["AUDIO"]}

    # 메모리 버퍼(WAV) 준비
    # WAV는 헤더에 전체 길이가 들어가므로 '완전 스트리밍'은 까다로움.
    # 여기선 메모리에 모은 뒤 한 번에 반환(가장 간단/안전).
    buf = io.BytesIO()

    # 간이 WAV writer
    import wave
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)   # 16-bit PCM
        wav.setframerate(24000)

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": user_text}]},
                turn_complete=True
            )

            turn = session.receive()
            async for _, response in async_enumerate(turn):
                if response.data is not None:
                    wav.writeframes(response.data)

    audio_bytes = buf.getvalue()
    return Response(content=audio_bytes, media_type="audio/wav")


# pip install fastapi uvicorn google-genai python-dotenv
# uvicorn server:app --reload --port 8000
