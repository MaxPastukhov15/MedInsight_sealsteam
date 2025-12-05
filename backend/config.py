from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

C = {
    "R": "\x1b[31m",
    "G": "\x1b[32m",
    "B": "\x1b[34m",
    "Y": "\x1b[33m",
    "C": "\x1b[36m",
    "M": "\x1b[35m",
    "GR": "\x1b[90m",
    "X": "\x1b[0m",
}


def log(tag: str, msg: str, color: str = "X"):
    from datetime import datetime

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C['GR']}[{ts}]{C[color]} [{tag}] {msg}{C['X']}")


class Config(BaseSettings):
    MAX_TOOL_CALLS: int = 8


cfg = Config()
