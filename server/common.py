# common.py (공용 유틸)
# - 환경변수 로드, 클라이언트 생성, WAV 헬퍼를 한군데 모아둡니다.
# - Windows에서 asyncio 정책 문제 대응 옵션도 포함했습니다. 

import os
import contextlib
import wave
from dotenv import load_dotenv
from google import genai

# 필요시 Windows 정책 설정 (주석 해제)
# import asyncio
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def load_api_key() -> str:
    # .env 우선 로드 → 환경변수 읽기
    load_dotenv(override=False)
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "환경변수 GOOGLE_API_KEY가 없습니다. .env 파일 또는 OS 환경변수에 키를 설정하세요."
        )
    return key

def make_client() -> genai.Client:
    api_key = load_api_key()
    return genai.Client(api_key=api_key)

@contextlib.contextmanager
def wave_file(filename: str, channels: int = 1, rate: int = 24000, sample_width: int = 2):
    """16-bit PCM .wav 파일 헬퍼"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)  # 16-bit
        wf.setframerate(rate)
        yield wf
