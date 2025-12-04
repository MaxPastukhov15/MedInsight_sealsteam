import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

C = {
    "R": "\x1B[31m", "G": "\x1B[32m", "B": "\x1B[34m",
    "Y": "\x1B[33m", "C": "\x1B[36m", "M": "\x1B[35m",
    "GR": "\x1B[90m", "X": "\x1B[0m"
}


def log(tag: str, msg: str, color: str = "X"):
    from datetime import datetime
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C['GR']}[{ts}]{C[color]} [{tag}] {msg}{C['X']}")


class Config(BaseSettings):
    MAX_TOOL_CALLS: int = 8


cfg = Config()
