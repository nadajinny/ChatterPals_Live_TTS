# server.py
import io
import os
import base64
import wave
import asyncio
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY가 비어있습니다. .env나 환경변수를 설정하세요.")

MODEL = "gemini-live-2.5-flash-preview"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 필요시 허용 도메인 제한 권장
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
    입력(JSON): {"text": "..."}
    출력(JSON): {"text": "...", "audio_b64": "...", "mime": "audio/wav"}
    """
    user_text = (payload.get("text") or "").strip()
    if not user_text:
        return JSONResponse(status_code=400, content={"error": "empty text"})

    # 오디오+텍스트 동시 요청
    config = {"response_modalities": ["AUDIO", "TEXT"]}

    # 메모리 버퍼에 WAV 쓰기
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)   # 16-bit PCM
        wav.setframerate(24000)

        text_chunks = []

        async with client.aio.live.connect(model=MODEL, config=config) as session:
            # 사용자 텍스트 전송
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": user_text}]},
                turn_complete=True
            )

            # 한 턴의 응답 스트림 수신
            turn = session.receive()
            async for _, response in async_enumerate(turn):
                # 오디오 데이터(PCM) → WAV 프레임으로 추가
                if getattr(response, "data", None) is not None:
                    wav.writeframes(response.data)
                # 텍스트 청크가 오면 수집
                if getattr(response, "text", None):
                    text_chunks.append(response.text)

    audio_bytes = buf.getvalue()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    text_full = "".join(text_chunks).strip()

    return JSONResponse({
        "text": text_full,
        "audio_b64": audio_b64,
        "mime": "audio/wav",
    })
