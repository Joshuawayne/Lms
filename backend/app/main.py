"""ASGI entry point used by Uvicorn."""

import asyncio
import sys

# On Windows, psycopg async requires SelectorEventLoop instead of ProactorEventLoop
if sys.platform == "win32" and sys.version_info < (3, 14):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.bootstrap import create_app

app = create_app()
