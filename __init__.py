from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, Event
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from .utils.exit_checker import exitCheck
from .utils.downloader import _downloadImgURL, _downloadImgFileid
from .utils.sender import *
from .utils.executor import *
from .utils.cleaner import *
import aiohttp
import aiofiles
import time
import os

from .config import *

getModelPrompt = "请发送想要使用的超分辨率模型序号: \n" \
    "1. realesrgan-x4plus \n" \
    "2. realesrgan-x4plus-anime (optimized for anime images, small model size)" 
#    "3. realesr-animevideov3 (animation video)"

gif_msg = "检测到图片为gif格式，该格式无法直接进行处理，请选择需要转化的格式类型：\n" \
    "1. jpg\n" \
    "2. png"

gif_ls = "接受到的图片为gif格式，将被自动输出为jpg格式..."

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
        image_size = os.path.getsize(savePath)
        # print(f"Image size: {image_size}")
        if image_size >= MAX_SIZE:
            await matcher.finish(f"检测到当前图片过大({image_size/1024/1024:.2f} MB)，超出可执行阈值：{MAX_SIZE/1024/1024} MB，当前操作已取消")
            return
        if image_size >= WARNING_SIZE:
            await matcher.send(f"检测到当前图片较大({image_size/1024/1024:.2f} MB)，可能花费较长时间")
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
    
    state["model"] = int(input)
    # await process_image(bot, event, state, matcher)

@superResolution.handle()
async def process_image(bot: Bot, event: Event, state: T_State, matcher: Matcher):
    image_path = state["image_path"]
    model = MODEL[state["model"]]
    filename = Path(image_path).name
    output_filename = "output_" + filename
    input_path = ROOT_DIR / INPUT_DIR / filename
    input_suffix = input_path.suffix

    # gif 处理
    if input_suffix.lower() == ".gif":
        print("isgif")
        await matcher.send(gif_ls)
        state["output_suffix"] = ".jpg"
    else:
        print("notgif")
        state["output_suffix"] = input_suffix

    output_path = (ROOT_DIR / OUTPUT_DIR / output_filename).with_suffix(state["output_suffix"])
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
        await matcher.finish("出现错误！会话进程已结束")
    

# @superResolution.got("target_suffix")
# async def get_suffix(bot: Bot, event: Event, state: T_State, matcher: Matcher):
#     print("in get_suffix")
#     await exitCheck(event, matcher)
#     msg = event.get_plaintext()
#     print(msg)
#     if msg not in {"1", "2"}:
#         await matcher.send("输入有误，请重新输入")
#         await matcher.reject_arg("target_suffix")
#     state["output_suffix"] = SUFFIX[int(msg)]
#     print(f"selected suffix: {SUFFIX[int(msg)]}")
