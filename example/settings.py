import os
from dotenv import load_dotenv
load_dotenv()

SOCKET = os.getenv("SOCKET", "127.0.0.1:8888")