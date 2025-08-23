import asyncio
from pathlib import Path
from nonebot import get_driver
from ..config import *

cleaner = get_driver()

RECEIVED_DIR = Path(ROOT_DIR / SAVE_DIR)
PROCESSED_DIR = Path(ROOT_DIR / OUTPUT_DIR)

@cleaner.on_startup
async def startup_task():
    asyncio.create_task(size_monitor())

async def size_monitor():
    while True:
        received_size = get_folder_size(RECEIVED_DIR)
        processed_size = get_folder_size(PROCESSED_DIR)
        if received_size > MAX_RECEIVED_FOLDER_SIZE:
            delete_files(RECEIVED_DIR, MAX_RECEIVED_FOLDER_SIZE)
            print(f"{UNIVERSAL_INFO_HEADER} Seccussfully clean the received directory, current size: {get_folder_size(RECEIVED_DIR)/1024/1024} MB")
        if processed_size > MAX_PROCESSED_FOLDER_SIZE:
            delete_files(PROCESSED_DIR, MAX_PROCESSED_FOLDER_SIZE)
            print(f"{UNIVERSAL_INFO_HEADER} Seccussfully clean the processed directory, current size: {get_folder_size(PROCESSED_DIR)/1024/1024} MB")
        await asyncio.sleep(10)


def get_folder_size(path: Path) -> int:
    size = 0
    for file in path.rglob("*"):
        if file.is_file():
            size += file.stat().st_size
    return size

def delete_files(path: Path, target_size: int):
    files = [item for item in path.rglob("*") if item.is_file()]
    files.sort(key=lambda f:f.stat().st_mtime)
    current_size = sum(file.stat().st_size for file in files)
    for file in files:
        if current_size <= target_size:
            break
        try:
            file_size = file.stat().st_size
            file.unlink()
            current_size -= file_size
        except Exception as e:
            print(f"[Delete Error] Fail to delete {file}: {e}")
    