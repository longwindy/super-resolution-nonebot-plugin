import aiohttp
import aiofiles
from nonebot.adapters.onebot.v11 import Bot

from ..config import *


async def _downloadImgURL(url: str, file_id :str) -> str:
    filename = file_id.strip()
    save_path = SAVE_DIR / filename
    save_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(save_path, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    return str(save_path)
        except Exception as e:
            print(f"[ERROR] Failed to download from url: {e}")
            return None


async def _downloadImgFileid(bot: Bot, file_id: str, filename: str = None) -> str | None:
    try:
        file_info = await bot.call_api("get_file", file_id = file_id)
        file_path = file_info.get("file")
        if not file_path:
            return None
        full_path = Path(file_path)
        if not full_path.exists():
            return None
        if not filename:
            filename = full_path.name
        save_path = SAVE_DIR / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)

        
        async with aiofiles.open(full_path, mode="rb") as src:
            content = await src.read()
            async with aiofiles.open(save_path, mode="wb") as dst:
                await dst.write(content)
        
        return str(save_path)
    except Exception as e:
        print(f"[ERROR] Failed to download from file_id: {e}")
        return None