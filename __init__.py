from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, Event
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from .utils.exit_checker import exitCheck
from .utils.downloader import _downloadImgURL, _downloadImgFileid
from .utils.sender import *
from .utils.executor import *
import aiohttp
import aiofiles
import time
import os

from .config import *

getModelPrompt = "请发送想要使用的超分辨率模型序号: \n" \
    "1. realesrgan-x4plus \n" \
    "2. realesrgan-x4plus-anime (optimized for anime images, small model size)" 
#    "3. realesr-animevideov3 (animation video)"

test = on_command("test", priority=10, block=True)

@test.handle()
async def handle_test():
    await test.finish("test successed")


superResolution = on_command("sr", aliases={"超分"}, priority=10, block=True)

@superResolution.handle()
async def _getImage(event: Event, state: T_State, matcher: Matcher):
    await matcher.send("请发送一张图片\nTips:你可以随时发送'0'退出操作")

@superResolution.got("image")
async def get_image(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await exitCheck(event, matcher)
    message: Message = event.get_message()

    isImage = False
    url = ""
    file_id = ""
    savePath = ""

    for seg in message:
        if seg.type == 'image':
            url = seg.data.get('url')
            file_id = seg.data.get('file')
            isImage = True
            savePath = await _downloadImgURL(url, file_id)
        elif seg.type == 'file':
            filename = seg.data.get("file") or ""
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
                url = seg.data.get("url")
                file_id = seg.data.get("file_id")
                isImage = True
                savePath = await _downloadImgFileid(bot=bot, file_id=file_id)
    if isImage:
        state["image_path"] = savePath
        # await matcher.send(f"收到了图片，file ID: {file_id}, url: {url}")
    else:
        await matcher.reject("你发送的不是图片，请重新发送")


@superResolution.got(key="model", prompt=getModelPrompt)
async def get_model(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    await exitCheck(event, matcher)
    message: Message = event.get_message()
    is_all_text = all(seg.type == "text" for seg in message)
    if not is_all_text:
        await matcher.reject("只接受文字输入，请重新发送")
    
    input = event.get_plaintext().strip()

    if input not in {"1", "2"}:
        await matcher.reject("请输入正确的选项编号")
    
    state["model"] = int(matcher.get_arg("model").extract_plain_text())
    await process_image(bot, event, state, matcher)


async def process_image(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    image_path = state["image_path"]
    model = MODEL[state["model"]]
    filename = Path(image_path).name
    output_filename = "output_" + filename
    input_path = ROOT_DIR / INPUT_DIR / filename
    output_path = ROOT_DIR / OUTPUT_DIR / output_filename
    exe_path = BASE_DIR / "SRTool" / "realesrgan-ncnn-vulkan.exe"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("before run")
    await matcher.send("超分运行中，整个过程需要一定时间，请坐和放宽...")

    start_time = time.time()

    async def executeSR(matcher: Matcher):
        quene = asyncio.Queue()
        execute_task = asyncio.create_task(run_exe(exe_path, quene, "-i", input_path, "-o", output_path, "-n", model))
        watcher_task = asyncio.create_task(sendEstimatedTime(matcher, quene))
        returncode = await execute_task
        await watcher_task
        return returncode
    
    returncode = await executeSR(matcher)
    print(f"returncode: {returncode}")
    end_time = time.time()
    if returncode == 0:
        elapsed = end_time - start_time
        matcher.state["output_image_abspath", "exe_time"] = output_path, elapsed
        image_size = os.path.getsize(output_path)
        if image_size <= MAX_SEND_IMAGE_SIZE:
            await send_by_image(bot, event, state, matcher)
        else:
            await send_by_file(bot, event, state, matcher)
    else:
        await matcher.finish("出现错误！对话进程已结束")
    

