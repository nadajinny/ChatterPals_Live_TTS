# audio_loop.py (원하시면 추가)
# python audio_loop.py
import asyncio
from common import make_client, wave_file

MODEL = "gemini-live-2.5-flash-preview"

async def async_enumerate(aiter):
    i = 0
    async for item in aiter:
        yield i, item
        i += 1

class AudioLoop:
    def __init__(self, model=MODEL, config=None):
        self.index = 0
        self.model = model
        self.config = config or {"response_modalities": ["AUDIO"]}

    async def run(self):
        client = make_client()
        async with client.aio.live.connect(model=self.model, config=self.config) as session:
            while True:
                text = await asyncio.to_thread(input, "message > ")
                if text.lower().strip() == "q":
                    print("Bye!")
                    break

                await session.send_client_content(
                    turns={"role": "user", "parts": [{"text": text}]},
                    turn_complete=True
                )

                file_name = f"audio_{self.index}.wav"
                self.index += 1
                with wave_file(file_name) as wav:
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
                print(f"\nSaved: {file_name}")

async def main():
    loop = AudioLoop()
    await loop.run()

if __name__ == "__main__":
    asyncio.run(main())
