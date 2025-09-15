# live_text.py (텍스트 <-> 텍스트)
# 실행 명령어 : python live_text.py
import asyncio
from google.genai import types
from common import make_client

MODEL = "gemini-live-2.5-flash-preview"  # Live API 지원 모델

async def main():
    client = make_client()

    config = {"response_modalities": ["TEXT"]}

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        msg = "Hello? Gemini are you there?"
        print("> ", msg)
        await session.send_client_content(
            turns={"role": "user", "parts": [{"text": msg}]},
            turn_complete=True
        )

        # 모델 한 턴이 완료될 때까지 스트리밍 수신
        turn = session.receive()
        async for chunk in turn:
            if chunk.text is not None:
                print("-", chunk.text)

if __name__ == "__main__":
    asyncio.run(main())
