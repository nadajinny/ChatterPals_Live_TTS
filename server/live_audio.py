# live_audio.py (텍스트 -> 오디오 : WAV 저장)
# 실행명령어 live_audio.py
import asyncio
from common import make_client, wave_file

MODEL = "gemini-live-2.5-flash-preview"

async def async_enumerate(aiter):
    i = 0
    async for item in aiter:
        yield i, item
        i += 1

async def main():
    client = make_client()
    config = {"response_modalities": ["AUDIO"]}

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        file_name = "reply.wav"
        with wave_file(file_name) as wav:
            message = "Hello! Please reply with a short greeting."
            print("> ", message)
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": message}]},
                turn_complete=True
            )

            # 오디오 청크를 받으면서 파일에 바로 기록
            turn = session.receive()
            async for n, response in async_enumerate(turn):
                if response.data is not None:
                    wav.writeframes(response.data)
                    if n == 0:
                        try:
                            mime = response.server_content.model_turn.parts[0].inline_data.mime_type
                            print("MIME:", mime)
                        except Exception:
                            pass
                    print(".", end="", flush=True)

        print(f"\nSaved: {file_name} — 시스템 기본 플레이어로 재생해 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())
