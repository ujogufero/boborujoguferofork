import os
import asyncio
from loguru import logger
from huum.huum import Huum


def get_sauna_status():
    async def _fetch_status():
        username = os.environ.get("HUUM_USERNAME", "")
        password = os.environ.get("HUUM_PASSWORD", "")
        huum = Huum(username=username, password=password)
        await huum.open_session()
        try:
            status = await huum.status()
            return status
        finally:
            await huum.close_session()

    try:
        return asyncio.run(_fetch_status())
    except Exception as e:
        logger.error(f"Error fetching sauna status: {e}")
        return None
