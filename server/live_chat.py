# live_chat.py
# 실행 명령어 python live_chat.py
import asyncio
from common import make_client

MODEL = "gemini-live-2.5-flash-preview"

async def main():
    client = make_client()
    config = {"response_modalities": ["TEXT"]}

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        print("Type 'q' to quit.\n")
        while True:
            # get user input
            user_input = await asyncio.to_thread(input, "You > ")
            if user_input.strip().lower() == "q":
                print("Bye!")
                break

            # send to model
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": user_input}]},
                turn_complete=True,
            )

            # collect response
            turn = session.receive()
            text_buf = []
            async for chunk in turn:
                if chunk.text is not None:
                    text_buf.append(chunk.text)

            full_text = "".join(text_buf).strip()
            print(f"Gemini > {full_text}\n")

if __name__ == "__main__":
    asyncio.run(main())
